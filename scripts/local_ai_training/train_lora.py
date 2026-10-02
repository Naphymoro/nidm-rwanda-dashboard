"""QLoRA fine-tuning of a small model on the engine-as-teacher examples, on one local GPU.

The loss covers only the assistant's answer: the model learns to answer like the engine, not to reproduce the prompt.
Thinking is off in the chat template, as in the Research Studio. Output: a LoRA adapter and, with --merge, a merged
model folder that Ollama can import (see README).

    python train_lora.py --data train.jsonl --base Qwen/Qwen3-1.7B --out runs/qwen3-1.7b-v1 --merge
    python train_lora.py --data train.jsonl tools.jsonl replay.jsonl --tools-schema tools_schema.json --lr 1e-4 \
        --out runs/qwen3-1.7b-v2 --merge

v1 (stage answers only, no tools in the prompt, lr 2e-4) became a copier that stopped calling tools. v2 mixes in tool
use and replay of the original model's own answers, renders every example with the Studio's tool list (as the model
sees it in use), and trains more gently.
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import torch
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments)

# The generator writes many identical "limits" answers; a balanced sample teaches the behaviours without drowning them.
MIX = {'explain': 450, 'cause': 150, 'forecast': 120, 'advice': 120, 'limits': 60,
       'tool_stage': 200, 'tool_propose': 60, 'tool_records': 60, 'tool_status': 60, 'next_answer': 150,
       'no_fake_confirm': 120, 'no_fake_add': 80, 'no_fake_review': 80, 'no_fake_decision': 120, 'replay': 200}
# v3: as many "it is your decision, use the card" replies as "run the next stage" calls (v2 learned "yes means act").


def balanced(rows, seed):
    by_kind = defaultdict(list)
    for row in rows:
        by_kind[row['kind']].append(row)
    rng = random.Random(seed)
    picked = []
    for kind, wanted in MIX.items():
        rng.shuffle(by_kind[kind])
        picked += by_kind[kind][:wanted]
    rng.shuffle(picked)
    return picked


def encode(tokenizer, row, max_len, tools=None):
    """Loss on the final assistant turn only, rendered by the model's own chat template (text or tool call)."""
    messages = row['messages']
    prompt = tokenizer.apply_chat_template(messages[:-1], tools=tools, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    full = tokenizer.apply_chat_template(messages, tools=tools, tokenize=False, enable_thinking=False)
    if not full.startswith(prompt):
        raise ValueError('chat template: the conversation does not extend the prompt; check the template')
    answer = full[len(prompt):]
    prompt_ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
    answer_ids = tokenizer(answer, add_special_tokens=False)['input_ids']
    ids = (prompt_ids + answer_ids)[-max_len:]
    labels = ([-100] * len(prompt_ids) + answer_ids)[-max_len:]
    return {'input_ids': ids, 'labels': labels}


def collate(batch, pad_id):
    width = max(len(item['input_ids']) for item in batch)
    ids = torch.full((len(batch), width), pad_id)
    labels = torch.full((len(batch), width), -100)
    mask = torch.zeros((len(batch), width), dtype=torch.long)
    for i, item in enumerate(batch):
        n = len(item['input_ids'])
        ids[i, :n] = torch.tensor(item['input_ids'])
        labels[i, :n] = torch.tensor(item['labels'])
        mask[i, :n] = 1
    return {'input_ids': ids, 'labels': labels, 'attention_mask': mask}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', nargs='+', required=True)
    parser.add_argument('--tools-schema', help='tool definitions shown in every prompt, as in the Studio')
    parser.add_argument('--base', default='Qwen/Qwen3-1.7B')
    parser.add_argument('--out', required=True)
    parser.add_argument('--epochs', type=float, default=1.0)
    parser.add_argument('--lr', type=float, default=2e-4)
    parser.add_argument('--rank', type=int, default=16)
    parser.add_argument('--max-len', type=int, default=3584)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--merge', action='store_true')
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.base)
    tools = json.load(open(args.tools_schema, encoding='utf-8')) if args.tools_schema else None
    rows = balanced([json.loads(line) for path in args.data for line in open(path, encoding='utf-8')], args.seed)
    data = [encode(tokenizer, row, args.max_len, tools) for row in rows]
    print('mix:', {kind: sum(1 for row in rows if row['kind'] == kind) for kind in MIX}, flush=True)
    print(f'{len(data)} examples; longest {max(len(d["input_ids"]) for d in data)} tokens; '
          f'answer tokens {sum(sum(l != -100 for l in d["labels"]) for d in data)}', flush=True)

    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.bfloat16,
                               bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.base, quantization_config=quant, torch_dtype=torch.bfloat16, device_map={'': 0})
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.rank * 2, lora_dropout=0.05, task_type='CAUSAL_LM',
                                             target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']))
    model.print_trainable_parameters()

    trainer = Trainer(
        model=model, train_dataset=data, data_collator=lambda batch: collate(batch, tokenizer.pad_token_id),
        args=TrainingArguments(output_dir=str(out / 'checkpoints'), per_device_train_batch_size=1, gradient_accumulation_steps=8,
                               num_train_epochs=args.epochs, learning_rate=args.lr, lr_scheduler_type='cosine', warmup_ratio=0.05,
                               logging_steps=10, save_strategy='no', bf16=True, gradient_checkpointing=True,
                               optim='paged_adamw_8bit', report_to=[], seed=args.seed, remove_unused_columns=False))
    trainer.train()
    model.save_pretrained(out / 'adapter')
    tokenizer.save_pretrained(out / 'adapter')
    (out / 'train_info.json').write_text(json.dumps({'base': args.base, 'examples': len(data), 'mix': MIX, 'tools': bool(tools), 'epochs': args.epochs,
                                                     'lr': args.lr, 'rank': args.rank, 'log': trainer.state.log_history}, indent=1))

    if args.merge:  # full-precision merge for Ollama import; the adapter alone is kept too
        del model, trainer
        torch.cuda.empty_cache()
        base = AutoModelForCausalLM.from_pretrained(args.base, torch_dtype=torch.bfloat16, device_map={'': 'cpu'})
        merged = PeftModel.from_pretrained(base, out / 'adapter').merge_and_unload()
        merged.save_pretrained(out / 'merged', safe_serialization=True)
        tokenizer.save_pretrained(out / 'merged')
        print('merged model ->', out / 'merged', flush=True)


if __name__ == '__main__':
    main()
