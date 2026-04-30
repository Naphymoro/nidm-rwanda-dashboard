import React, { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import {
  Upload,
  X,
  FileText,
  CheckCircle,
  AlertCircle,
  FileSpreadsheet,
} from "lucide-react";
import {
  ParsedNarrative,
  parseCsv,
  parseNarrativeText,
} from "@/lib/narrativeParser";

interface UploadedFile {
  id: string;
  name: string;
  type: "csv" | "narrative" | "unknown";
  size: number;
  uploadedAt: Date;
  status: "success" | "error";
  message?: string;
  parsedCount?: number;
}

interface FileUploadPanelProps {
  onNarrativesParsed?: (narratives: ParsedNarrative[]) => void;
}

function getFileType(filename: string): "csv" | "narrative" | "unknown" {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (ext === "csv") return "csv";
  if (ext === "txt" || ext === "md") return "narrative";
  return "unknown";
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

export default function FileUploadPanel({
  onNarrativesParsed,
}: FileUploadPanelProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    await processFiles(e.dataTransfer.files);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) await processFiles(e.target.files);
  };

  const processFiles = async (fileList: FileList) => {
    const newFiles: UploadedFile[] = [];
    const allParsed: ParsedNarrative[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const fileType = getFileType(file.name);
      const baseId = `${Date.now()}-${i}-${file.name}`;

      if (fileType === "unknown") {
        newFiles.push({
          id: baseId,
          name: file.name,
          type: "unknown",
          size: file.size,
          uploadedAt: new Date(),
          status: "error",
          message: "Unsupported file type. Use CSV, TXT, or MD.",
        });
        continue;
      }

      try {
        const text = await file.text();
        const parsed =
          fileType === "csv"
            ? parseCsv(text, file.name)
            : parseNarrativeText(text, file.name);

        if (parsed.length === 0) {
          newFiles.push({
            id: baseId,
            name: file.name,
            type: fileType,
            size: file.size,
            uploadedAt: new Date(),
            status: "error",
            message: "File parsed but contained no narratives.",
          });
        } else {
          allParsed.push(...parsed);
          newFiles.push({
            id: baseId,
            name: file.name,
            type: fileType,
            size: file.size,
            uploadedAt: new Date(),
            status: "success",
            message: `Parsed ${parsed.length} narrative${parsed.length === 1 ? "" : "s"}`,
            parsedCount: parsed.length,
          });
        }
      } catch (err) {
        newFiles.push({
          id: baseId,
          name: file.name,
          type: fileType,
          size: file.size,
          uploadedAt: new Date(),
          status: "error",
          message:
            err instanceof Error ? `Parse error: ${err.message}` : "Parse error",
        });
      }
    }

    setFiles((prev) => [...prev, ...newFiles]);
    if (allParsed.length > 0) onNarrativesParsed?.(allParsed);
  };

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClearAll = () => setFiles([]);

  const totalParsed = files.reduce((s, f) => s + (f.parsedCount ?? 0), 0);
  const successCount = files.filter((f) => f.status === "success").length;

  return (
    <div className="space-y-6">
      <div className="glass-dark border border-border/50 rounded-lg p-6 glow-primary">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold neon-text">File Upload</h3>
          <span className="text-xs text-muted-foreground">
            CSV, TXT, MD supported
          </span>
        </div>

        {/* Drag and Drop Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer ${
            isDragActive
              ? "border-primary bg-primary/10 glow-primary"
              : "border-border/50 bg-background/30 hover:border-primary/60 hover:bg-primary/5"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".csv,.txt,.md"
            onChange={handleFileSelect}
            className="hidden"
          />

          <Upload className="w-12 h-12 mx-auto mb-4 text-primary/70 animate-float" />
          <h4 className="text-lg font-semibold text-foreground mb-2">
            Drop CSV or narrative files here
          </h4>
          <p className="text-sm text-muted-foreground mb-1">
            or click to browse your computer
          </p>
          <p className="text-xs text-muted-foreground">
            Files are parsed locally in your browser, then added to the Narrative Library below.
          </p>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-foreground">
                Uploaded Files ({files.length})
              </h4>
              <button
                onClick={handleClearAll}
                className="text-xs text-muted-foreground hover:text-destructive transition-colors"
              >
                Clear All
              </button>
            </div>

            <div className="space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className={`flex items-start gap-3 p-3 rounded-md border transition-all duration-200 ${
                    file.status === "success"
                      ? "bg-primary/5 border-primary/30"
                      : "bg-destructive/10 border-destructive/30"
                  }`}
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {file.type === "csv" ? (
                      <FileSpreadsheet className="w-5 h-5 text-primary" />
                    ) : file.type === "narrative" ? (
                      <FileText className="w-5 h-5 text-accent" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-destructive" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-medium text-foreground truncate">
                        {file.name}
                      </p>
                      {file.status === "success" && (
                        <CheckCircle className="w-4 h-4 text-primary flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>{file.uploadedAt.toLocaleTimeString()}</span>
                      {file.parsedCount !== undefined && (
                        <>
                          <span>•</span>
                          <span className="text-primary font-semibold">
                            {file.parsedCount} parsed
                          </span>
                        </>
                      )}
                    </div>
                    {file.message && (
                      <p
                        className={`text-xs mt-1 ${
                          file.status === "success"
                            ? "text-primary"
                            : "text-destructive"
                        }`}
                      >
                        {file.message}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveFile(file.id)}
                    className="p-1 hover:bg-white/10 rounded transition-colors flex-shrink-0"
                    title="Remove file"
                  >
                    <X className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* File Statistics */}
        {files.length > 0 && (
          <div className="mt-6 pt-6 border-t border-border/50 grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Files</p>
              <p className="text-2xl font-bold text-foreground">{files.length}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Successful</p>
              <p className="text-2xl font-bold text-primary">{successCount}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Narratives parsed</p>
              <p className="text-2xl font-bold text-accent">{totalParsed}</p>
            </div>
          </div>
        )}
      </div>

      {/* File Format Guide */}
      <Card className="glass-dark border-border/50 p-6">
        <h4 className="text-sm font-semibold text-foreground mb-4">
          File Format Guide
        </h4>
        <div className="space-y-4 text-sm">
          <div>
            <p className="font-medium text-primary mb-1">CSV Format</p>
            <p className="text-muted-foreground text-xs">
              Header row required. Columns: key, label, type, quote, E, C, tau, kappa, targets
            </p>
            <code className="text-xs bg-background/50 p-2 rounded block mt-2 text-primary font-mono">
              key,label,type,quote,E,C,tau,kappa,targets<br />
              n_001,Health Benefits,story,"Clean cooking saves lives",0.8,0.7,0.9,0.8,all
            </code>
          </div>
          <div>
            <p className="font-medium text-accent mb-1">Narrative Format (TXT / MD)</p>
            <p className="text-muted-foreground text-xs">
              Each paragraph (separated by a blank line) becomes one narrative entry. Heuristic
              E, C, τ, κ scores are assigned automatically; you can edit them later.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
