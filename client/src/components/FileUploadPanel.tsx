import React, { useRef, useState } from "react";
import {
  AlertCircle,
  Braces,
  CheckCircle,
  Clipboard,
  Database,
  FileJson,
  FileSpreadsheet,
  FileText,
  ShieldCheck,
  Upload,
  X,
} from "lucide-react";
import {
  parseCsv,
  parseNarrativeText,
  parseSdmxNarratives,
  type ParsedNarrative,
} from "@/lib/narrativeParser";
import {
  buildSdmxGateReport,
  buildSdmxNarrativePayload,
  type NarrativeInputFormat,
  type SdmxGateReport,
  type SdmxNarrativePayload,
} from "@/lib/sdmxGate";

interface UploadedFile {
  id: string;
  name: string;
  type: NarrativeInputFormat | "unknown";
  size: number;
  uploadedAt: Date;
  status: "success" | "error";
  message?: string;
  parsedCount?: number;
  gate?: SdmxGateReport;
  payload?: SdmxNarrativePayload;
}

interface FileUploadPanelProps {
  onNarrativesParsed?: (narratives: ParsedNarrative[]) => void;
}

function getFileType(filename: string): NarrativeInputFormat | "unknown" {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (ext === "csv") return "csv";
  if (ext === "txt" || ext === "md") return "narrative";
  if (ext === "json" || ext === "xml" || ext === "sdmx") return "sdmx";
  return "unknown";
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`;
}

function parseByType(
  fileType: NarrativeInputFormat,
  text: string,
  filename: string
): ParsedNarrative[] {
  if (fileType === "csv") return parseCsv(text, filename);
  if (fileType === "sdmx") return parseSdmxNarratives(text, filename);
  return parseNarrativeText(text, filename);
}

function typeLabel(type: UploadedFile["type"]) {
  if (type === "csv") return "CSV table";
  if (type === "narrative") return "Narrative text";
  if (type === "sdmx") return "SDMX exchange";
  return "Unsupported";
}

function FileIcon({ type }: { type: UploadedFile["type"] }) {
  if (type === "csv") return <FileSpreadsheet className="h-5 w-5 text-[var(--gold)]" />;
  if (type === "sdmx") return <FileJson className="h-5 w-5 text-[var(--sky)]" />;
  if (type === "narrative") return <FileText className="h-5 w-5 text-[var(--verdant)]" />;
  return <AlertCircle className="h-5 w-5 text-[var(--flame)]" />;
}

export default function FileUploadPanel({
  onNarrativesParsed,
}: FileUploadPanelProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const [pasteText, setPasteText] = useState("");
  const [pasteName, setPasteName] = useState("field-notes.txt");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const registerParsedBatch = (
    parsed: ParsedNarrative[],
    fileType: NarrativeInputFormat,
    filename: string,
    size: number,
    id: string
  ): UploadedFile => {
    const gate = buildSdmxGateReport(parsed, fileType, filename);
    const payload = gate.accepted
      ? buildSdmxNarrativePayload(parsed, filename, gate.exchangeId)
      : undefined;

    if (gate.accepted && parsed.length > 0) {
      onNarrativesParsed?.(parsed);
    }

    return {
      id,
      name: filename,
      type: fileType,
      size,
      uploadedAt: new Date(),
      status: gate.accepted ? "success" : "error",
      message: gate.accepted
        ? `SDMX gate accepted ${parsed.length} observation${parsed.length === 1 ? "" : "s"}.`
        : gate.errors[0] ?? "SDMX gate rejected this file.",
      parsedCount: parsed.length,
      gate,
      payload,
    };
  };

  const processFiles = async (fileList: FileList) => {
    const nextFiles: UploadedFile[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const fileType = getFileType(file.name);
      const baseId = `${Date.now()}-${i}-${file.name}`;

      if (fileType === "unknown") {
        nextFiles.push({
          id: baseId,
          name: file.name,
          type: "unknown",
          size: file.size,
          uploadedAt: new Date(),
          status: "error",
          message: "Unsupported input. Use CSV, TXT, MD, JSON, XML, or SDMX.",
        });
        continue;
      }

      try {
        const text = await file.text();
        const parsed = parseByType(fileType, text, file.name);
        nextFiles.push(registerParsedBatch(parsed, fileType, file.name, file.size, baseId));
      } catch (err) {
        nextFiles.push({
          id: baseId,
          name: file.name,
          type: fileType,
          size: file.size,
          uploadedAt: new Date(),
          status: "error",
          message: err instanceof Error ? `Parse error: ${err.message}` : "Parse error",
        });
      }
    }

    setFiles((prev) => [...nextFiles, ...prev]);
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);
    await processFiles(event.dataTransfer.files);
  };

  const handleDrag = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(event.type === "dragenter" || event.type === "dragover");
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) await processFiles(event.target.files);
    event.target.value = "";
  };

  const handlePasteIngest = () => {
    const id = `paste-${Date.now()}`;
    const filename = pasteName.trim() || "pasted-narratives.txt";
    const parsed = parseNarrativeText(pasteText, filename);
    const entry = registerParsedBatch(
      parsed,
      "narrative",
      filename,
      new Blob([pasteText]).size,
      id
    );
    setFiles((prev) => [entry, ...prev]);
    if (entry.status === "success") setPasteText("");
  };

  const copyPayload = async (file: UploadedFile) => {
    if (!file.payload) return;
    await navigator.clipboard.writeText(JSON.stringify(file.payload, null, 2));
    setCopiedId(file.id);
    window.setTimeout(() => setCopiedId(null), 1600);
  };

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const totalParsed = files.reduce((sum, file) => sum + (file.parsedCount ?? 0), 0);
  const acceptedCount = files.filter((file) => file.status === "success").length;
  const lastGate = files.find((file) => file.gate)?.gate;

  return (
    <div className="space-y-6">
      <section className="nidm-card p-5">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="font-mono-data text-[10px] uppercase tracking-[1.5px] text-[var(--t4)]">
              Loading gate
            </p>
            <h3 className="font-syne text-xl font-bold">Narrative ingest and SDMX exchange</h3>
            <p className="mt-2 max-w-3xl text-sm text-[var(--t3)]">
              Upload CSV, narrative text, Markdown, or SDMX-style JSON/XML. Every batch is
              validated into the same input/output contract before it reaches the model.
            </p>
          </div>
          <div className="rounded-lg border border-[rgba(32,201,151,.25)] bg-[rgba(32,201,151,.08)] px-3 py-2 text-right">
            <div className="font-mono-data text-[10px] uppercase tracking-[1px] text-[var(--verdant)]">
              Gate status
            </div>
            <div className="font-syne text-lg font-bold text-[var(--t1)]">
              {lastGate ? (lastGate.accepted ? "Accepted" : "Blocked") : "Ready"}
            </div>
          </div>
        </div>

        <div className="grid gap-3 lg:grid-cols-3">
          <GateStep
            icon={<Upload className="h-4 w-4" />}
            label="Input"
            value="CSV, TXT, MD, JSON, XML"
            accent="var(--gold)"
          />
          <GateStep
            icon={<ShieldCheck className="h-4 w-4" />}
            label="SDMX gate"
            value="dimensions + measures validated"
            accent="var(--sky)"
          />
          <GateStep
            icon={<Database className="h-4 w-4" />}
            label="Output"
            value="SDMX-NIDM observation payload"
            accent="var(--verdant)"
          />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_.95fr]">
        <div className="nidm-card p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h4 className="font-syne text-lg font-bold">File upload</h4>
              <p className="text-xs text-[var(--t3)]">Local parsing; accepted files go straight into the library.</p>
            </div>
            <span className="font-mono-data rounded-md border border-[var(--bdr)] bg-[var(--deep)] px-2 py-1 text-[10px] text-[var(--t3)]">
              .csv .txt .md .json .xml .sdmx
            </span>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer rounded-lg border border-dashed p-8 text-center transition ${
              isDragActive
                ? "border-[var(--indigoL)] bg-[rgba(59,91,219,.14)]"
                : "border-[var(--bdrV)] bg-[var(--deep)] hover:border-[var(--indigoL)]"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".csv,.txt,.md,.json,.xml,.sdmx"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Upload className="mx-auto mb-4 h-10 w-10 text-[var(--indigoL)]" />
            <h5 className="font-syne text-lg font-bold">Drop narrative evidence here</h5>
            <p className="mt-2 text-sm text-[var(--t3)]">
              Rows, paragraphs, and SDMX observations are normalized into E, C, tau, kappa, and Phi.
            </p>
          </div>
        </div>

        <div className="nidm-card p-5">
          <div className="mb-4">
            <h4 className="font-syne text-lg font-bold">Paste multi-paragraph narratives</h4>
            <p className="text-xs text-[var(--t3)]">
              Blank-line separated paragraphs become separate observations; single-line notes are split line by line.
            </p>
          </div>
          <label className="font-mono-data mb-2 block text-[10px] uppercase tracking-[1px] text-[var(--t3)]">
            Source name
          </label>
          <input
            value={pasteName}
            onChange={(event) => setPasteName(event.target.value)}
            className="mb-3 h-10 w-full rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 text-sm text-[var(--t1)] outline-none transition focus:border-[var(--indigoL)]"
          />
          <textarea
            value={pasteText}
            onChange={(event) => setPasteText(event.target.value)}
            placeholder={"Paste interview notes, radio transcripts, community feedback, or policy brief excerpts..."}
            className="min-h-36 w-full resize-none rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-3 text-sm text-[var(--t1)] outline-none transition placeholder:text-[var(--t4)] focus:border-[var(--indigoL)]"
          />
          <button
            type="button"
            onClick={handlePasteIngest}
            disabled={!pasteText.trim()}
            className="mt-3 inline-flex h-10 items-center gap-2 rounded-lg border border-[rgba(32,201,151,.3)] bg-[rgba(32,201,151,.12)] px-4 text-sm font-semibold text-[var(--verdant)] transition hover:bg-[rgba(32,201,151,.18)] disabled:cursor-not-allowed disabled:opacity-45"
          >
            <Braces className="h-4 w-4" />
            Ingest text through SDMX gate
          </button>
        </div>
      </section>

      <section className="nidm-card p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h4 className="font-syne text-lg font-bold">Gate history</h4>
            <p className="text-xs text-[var(--t3)]">
              Accepted batches can copy their SDMX-NIDM output payload for export or API handoff.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <MiniStat label="Files" value={files.length.toString()} />
            <MiniStat label="Accepted" value={acceptedCount.toString()} />
            <MiniStat label="Observed" value={totalParsed.toString()} />
          </div>
        </div>

        {files.length === 0 ? (
          <div className="rounded-lg border border-dashed border-[var(--bdrV)] bg-[var(--deep)] p-8 text-center">
            <Database className="mx-auto mb-3 h-8 w-8 text-[var(--t4)]" />
            <p className="text-sm text-[var(--t3)]">No input batches have passed through the gate yet.</p>
          </div>
        ) : (
          <div className="max-h-[430px] space-y-3 overflow-y-auto pr-1">
            {files.map((file) => (
              <div
                key={file.id}
                className={`rounded-lg border p-4 ${
                  file.status === "success"
                    ? "border-[rgba(32,201,151,.25)] bg-[rgba(32,201,151,.06)]"
                    : "border-[rgba(255,107,53,.28)] bg-[rgba(255,107,53,.07)]"
                }`}
              >
                <div className="flex items-start gap-3">
                  <FileIcon type={file.type} />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h5 className="truncate text-sm font-semibold text-[var(--t1)]">{file.name}</h5>
                      <span className="font-mono-data rounded border border-[var(--bdr)] bg-[var(--deep)] px-1.5 py-0.5 text-[10px] uppercase tracking-[.8px] text-[var(--t3)]">
                        {typeLabel(file.type)}
                      </span>
                      {file.status === "success" ? (
                        <CheckCircle className="h-4 w-4 text-[var(--verdant)]" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-[var(--flame)]" />
                      )}
                    </div>

                    <div className="font-mono-data mt-2 flex flex-wrap gap-3 text-[11px] text-[var(--t3)]">
                      <span>{formatFileSize(file.size)}</span>
                      <span>{file.uploadedAt.toLocaleTimeString()}</span>
                      <span>{file.parsedCount ?? 0} observations</span>
                      {file.gate && <span>{file.gate.exchangeId}</span>}
                    </div>

                    <p className={`mt-2 text-xs ${file.status === "success" ? "text-[var(--verdant)]" : "text-[var(--flame)]"}`}>
                      {file.message}
                    </p>

                    {file.gate && (
                      <div className="mt-3 grid gap-2 md:grid-cols-2">
                        <GateMeta label="Dimensions" value={file.gate.dimensions.join(", ")} />
                        <GateMeta label="Measures" value={file.gate.measures.join(", ")} />
                      </div>
                    )}

                    {file.gate?.warnings.length ? (
                      <div className="mt-3 rounded-md border border-[rgba(245,159,0,.25)] bg-[rgba(245,159,0,.08)] p-2 text-xs text-[var(--goldL)]">
                        {file.gate.warnings.slice(0, 2).join(" ")}
                      </div>
                    ) : null}
                  </div>

                  <div className="flex shrink-0 items-center gap-1">
                    {file.payload && (
                      <button
                        type="button"
                        onClick={() => copyPayload(file)}
                        className="rounded-md p-2 text-[var(--t3)] transition hover:bg-white/10 hover:text-[var(--t1)]"
                        title="Copy SDMX-NIDM output payload"
                      >
                        <Clipboard className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(file.id)}
                      className="rounded-md p-2 text-[var(--t3)] transition hover:bg-white/10 hover:text-[var(--flame)]"
                      title="Remove from history"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {copiedId === file.id && (
                  <div className="font-mono-data mt-3 text-[11px] text-[var(--indigoL)]">
                    SDMX-NIDM payload copied.
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function GateStep({
  icon,
  label,
  value,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="rounded-lg border border-[var(--bdr)] bg-[var(--deep)] p-4">
      <div
        className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg"
        style={{ color: accent, background: `color-mix(in srgb, ${accent} 14%, transparent)` }}
      >
        {icon}
      </div>
      <div className="font-mono-data text-[10px] uppercase tracking-[1.3px] text-[var(--t4)]">{label}</div>
      <div className="mt-1 text-sm font-semibold text-[var(--t1)]">{value}</div>
    </div>
  );
}

function GateMeta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2">
      <div className="font-mono-data text-[9px] uppercase tracking-[1px] text-[var(--t4)]">{label}</div>
      <div className="font-mono-data mt-1 truncate text-[11px] text-[var(--t2)]">{value}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-16 rounded-lg border border-[var(--bdr)] bg-[var(--deep)] px-3 py-2">
      <div className="font-mono-data text-[9px] uppercase tracking-[1px] text-[var(--t4)]">{label}</div>
      <div className="font-syne text-lg font-bold text-[var(--t1)]">{value}</div>
    </div>
  );
}
