"""Lessons use real harness runs; progress requires an executed experiment and a check."""
SAMPLE = '''SYNTHETIC INTERVIEW SET — ENERGY JUST TRANSITION — FOR DEMONSTRATION ONLY

Interview 1, small enterprise owner: Reliable electricity would help me extend
working hours, but connection charges and unpredictable outages make planning
difficult. I support cleaner energy if the tariff remains affordable.

Interview 2, rural household: Solar lighting has made evening study easier and
reduced kerosene use. The biggest concern is the cost of replacing batteries and
finding someone nearby who can repair the system.

Interview 3, traditional-fuel worker: A rapid shift to new energy systems could
reduce my income. I would support the transition if training and alternative work
were available before the old work disappears.

Interview 4, community representative: Residents want cleaner and more reliable
energy, but projects should be discussed locally first. Fair access, transparent
pricing and visible community benefits matter.'''
LESSONS = [
    {'id': 'evidence', 'number': '01', 'title': 'From story to evidence', 'subtitle': 'Understand what a heuristic can—and cannot—tell you.',
     'duration': '8 min', 'level': 'Foundation', 'skill': 'evidence',
     'question': 'Which trust and adoption barriers appear in this field note?',
     'concept': 'Encoding turns observations into structured interpretations. Keyword scores are a starting point for review, not validated measurements of trust or proof of misinformation.',
     'instructions': ['Run the synthetic field note through the evidence workflow.', 'Inspect the encoding and diagnosis under Tool outputs.', 'Compare the signals with the original words before answering the check.'],
     'check': 'What does the trust score establish?',
     'choices': ['A keyword-derived interpretation that needs review', 'The measured trust of the population', 'Proof that the narrative is true'],
     'answer': 0, 'explanation': 'The score comes from an English keyword heuristic applied to one narrative. It does not estimate population trust or verify a claim.'},
    {'id': 'scenario', 'number': '02', 'title': 'Build a controlled comparison', 'subtitle': 'Change one assumption. Inspect both trajectories.',
     'duration': '12 min', 'level': 'Applied', 'skill': 'scenario',
     'question': 'How does an intervention change illustrative adoption under matching assumptions?',
     'concept': 'A baseline and intervention should share evidence, horizon, model family, and parameters. This experiment varies intervention strength only. Both trajectories remain illustrative.',
     'instructions': ['Review the paired model plan and execute it.', 'Open the Workbench to inspect the trajectories and numerical checks.', 'Create a follow-up with intervention strength zero; the two trajectories should match.'],
     'check': 'When intervention strength is zero, what should happen?',
     'choices': ['The intervention must always outperform baseline', 'Both deterministic trajectories should match', 'The baseline becomes a population forecast'],
     'answer': 1, 'explanation': 'With equal inputs and zero intervention, deterministic model trajectories match. This checks consistency, not real-world predictive validity.'},
    {'id': 'sensitivity', 'number': '03', 'title': 'Test the assumptions', 'subtitle': 'Explore sensitivity without mistaking it for uncertainty.',
     'duration': '15 min', 'level': 'Research', 'skill': 'sensitivity',
     'question': 'How sensitive is the model endpoint to intervention strength?',
     'concept': 'A one-parameter sweep evaluates a fixed grid of intervention strengths. A denser grid gives more resolution; it does not create new evidence or statistical confidence.',
     'instructions': ['Choose an execution profile and inspect the proposed grid.', 'Execute the sweep and compare endpoint adoption across strengths.', 'Read the scientific checks and export the complete audit bundle.'],
     'check': 'What does a denser sensitivity grid provide?',
     'choices': ['A calibrated causal estimate', 'A statistical confidence interval', 'More resolution over the selected parameter range'],
     'answer': 2, 'explanation': 'The grid is deterministic exploration over one parameter. Neither grid density nor numerical consistency validates the model against field data.'},
]


def public_lessons():
    return [{k: v for k, v in lesson.items() if k not in {'answer', 'explanation'}} for lesson in LESSONS]
