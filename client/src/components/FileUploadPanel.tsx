import React, { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, X, FileText, CheckCircle } from "lucide-react";

interface UploadedFile {
  id: string;
  name: string;
  type: "csv" | "narrative" | "unknown";
  size: number;
  uploadedAt: Date;
  status: "success" | "error";
  message?: string;
}

interface FileUploadPanelProps {
  onFilesUpload?: (files: UploadedFile[]) => void;
}

export default function FileUploadPanel({
  onFilesUpload,
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

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const droppedFiles = e.dataTransfer.files;
    processFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(e.target.files);
    }
  };

  const processFiles = (fileList: FileList) => {
    const newFiles: UploadedFile[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const fileType = getFileType(file.name);

      if (fileType !== "unknown") {
        const uploadedFile: UploadedFile = {
          id: `${Date.now()}-${i}`,
          name: file.name,
          type: fileType,
          size: file.size,
          uploadedAt: new Date(),
          status: "success",
          message: `${fileType === "csv" ? "CSV" : "Narrative"} file uploaded successfully`,
        };
        newFiles.push(uploadedFile);
      } else {
        const uploadedFile: UploadedFile = {
          id: `${Date.now()}-${i}`,
          name: file.name,
          type: "unknown",
          size: file.size,
          uploadedAt: new Date(),
          status: "error",
          message: "Unsupported file type. Please upload CSV or narrative files.",
        };
        newFiles.push(uploadedFile);
      }
    }

    setFiles((prev) => [...prev, ...newFiles]);
    onFilesUpload?.(newFiles);
  };

  const getFileType = (filename: string): "csv" | "narrative" | "unknown" => {
    const ext = filename.split(".").pop()?.toLowerCase();
    if (ext === "csv") return "csv";
    if (ext === "txt" || ext === "md") return "narrative";
    return "unknown";
  };

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClearAll = () => {
    setFiles([]);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="glass-dark border border-border/50 rounded-lg p-6 glow-primary">
        <h3 className="text-lg font-bold neon-text mb-6">File Upload</h3>

        {/* Drag and Drop Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer ${
            isDragActive
              ? "border-primary bg-primary/10"
              : "border-border/50 bg-background/50 hover:border-primary/50"
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".csv,.txt,.md"
            onChange={handleFileSelect}
            className="hidden"
          />

          <Upload className="w-12 h-12 mx-auto mb-4 text-primary/60" />
          <h4 className="text-lg font-semibold text-foreground mb-2">
            Drag and drop files here
          </h4>
          <p className="text-sm text-muted-foreground mb-4">
            or click to select files from your computer
          </p>
          <p className="text-xs text-muted-foreground">
            Supported formats: CSV, TXT, MD (Narrative files)
          </p>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-semibold text-foreground">
                Uploaded Files ({files.length})
              </h4>
              {files.length > 0 && (
                <button
                  onClick={handleClearAll}
                  className="text-xs text-muted-foreground hover:text-destructive transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>

            <div className="space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className={`flex items-start gap-3 p-3 rounded-lg border transition-all duration-200 ${
                    file.status === "success"
                      ? "bg-chart-3/10 border-chart-3/30"
                      : "bg-destructive/10 border-destructive/30"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                      <p className="text-sm font-medium text-foreground truncate">
                        {file.name}
                      </p>
                      {file.status === "success" && (
                        <CheckCircle className="w-4 h-4 text-chart-3 flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>{file.uploadedAt.toLocaleTimeString()}</span>
                    </div>
                    {file.message && (
                      <p
                        className={`text-xs mt-1 ${
                          file.status === "success"
                            ? "text-chart-3"
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
              <p className="text-xs text-muted-foreground mb-1">Total Files</p>
              <p className="text-2xl font-bold text-primary">{files.length}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Successful</p>
              <p className="text-2xl font-bold text-chart-3">
                {files.filter((f) => f.status === "success").length}
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Total Size</p>
              <p className="text-2xl font-bold text-secondary">
                {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}
              </p>
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
              Columns: key, label, type, quote, E, C, tau, kappa, targets
            </p>
            <code className="text-xs bg-background/50 p-2 rounded block mt-1 text-chart-3">
              narrative_1,Health Benefits,story,"Clean cooking saves lives",0.8,0.7,0.9,0.8,all
            </code>
          </div>
          <div>
            <p className="font-medium text-accent mb-1">Narrative Format (TXT/MD)</p>
            <p className="text-muted-foreground text-xs">
              Plain text or Markdown files containing narrative content
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
