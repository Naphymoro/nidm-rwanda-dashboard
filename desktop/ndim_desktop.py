from __future__ import annotations

import json
import logging
import os
import shutil
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
import zipfile
from pathlib import Path
from tkinter import BOTH, DISABLED, NORMAL, Button, Label, StringVar, Tk, filedialog, messagebox


APP_TITLE = "NDIM Engine"
HOST = "127.0.0.1"


def resource_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return Path(__file__).resolve().parents[1]


def platform_data_dir() -> Path:
    override = os.getenv("NDIM_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    home = Path.home()
    if sys.platform.startswith("win"):
        return Path(os.getenv("APPDATA") or home / "AppData" / "Roaming") / APP_TITLE
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_TITLE
    return Path(os.getenv("XDG_DATA_HOME") or home / ".local" / "share") / "ndim-engine"


def ensure_dirs() -> dict[str, Path]:
    base = platform_data_dir()
    paths = {
        "data": base,
        "uploads": base / "uploads",
        "exports": base / "exports",
        "logs": base / "logs",
        "sdmx": base / "sdmx",
        "backups": base / "backups",
        "support": base / "support",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def find_port(start: int = 8010) -> int:
    for port in range(start, start + 60):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((HOST, port)) != 0:
                return port
    raise RuntimeError("No free local port found for NDIM Engine")


def open_folder(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        os.system(f'open "{path}"')
    else:
        os.system(f'xdg-open "{path}"')


class DesktopApp:
    def __init__(self) -> None:
        self.root_dir = resource_root()
        self.paths = ensure_dirs()
        self.log_path = self.paths["logs"] / f"ndim-desktop-{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}.log"
        self.log(f"Launcher init: resource_root={self.root_dir}")
        self.port = find_port()
        self.url = f"http://{HOST}:{self.port}/?desktop=1"
        self.server = None
        self.server_thread: threading.Thread | None = None
        self.opened = False
        self.log(f"Launcher selected port {self.port}")

        backend_dir = self.root_dir / "backend"
        sys.path.insert(0, str(backend_dir))
        os.environ["NDIM_DESKTOP"] = "1"
        os.environ["NDIM_DATA_DIR"] = str(self.paths["data"])
        os.environ["NDIM_BUNDLED_ROOT"] = str(self.root_dir)
        self.log("Launcher environment configured")

        self.log("Creating Tk window")
        self.window = Tk()
        self.log("Tk window created")
        self.window.title(APP_TITLE)
        self.window.geometry("620x430")
        self.window.minsize(560, 390)
        self.window.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.status = StringVar(value="Starting local NDIM backend in offline-first mode...")
        self.url_text = StringVar(value=self.url)
        self.path_text = StringVar(value=str(self.paths["data"]))
        self._build_ui()
        self.log("Launcher UI built")

    def _build_ui(self) -> None:
        Label(self.window, text=APP_TITLE, font=("Segoe UI", 20, "bold")).pack(pady=(18, 4))
        Label(
            self.window,
            text="Local-first narrative evidence, modelling, and policy workflow.",
            wraplength=500,
        ).pack(pady=(0, 12))
        Label(self.window, textvariable=self.status, wraplength=500, fg="#375a2f").pack(pady=4)
        Label(self.window, textvariable=self.url_text, wraplength=500, fg="#1d4ed8").pack(pady=4)
        Label(self.window, text="Local data folder:", font=("Segoe UI", 9, "bold")).pack(pady=(14, 0))
        Label(self.window, textvariable=self.path_text, wraplength=500).pack(pady=(0, 10))

        self.open_app_button = Button(self.window, text="Open NDIM Engine", command=self.open_app, state=DISABLED)
        self.open_app_button.pack(fill=BOTH, padx=34, pady=4)
        Button(self.window, text="Check offline readiness", command=self.health_check).pack(fill=BOTH, padx=34, pady=4)
        Button(self.window, text="Open data folder", command=lambda: open_folder(self.paths["data"])).pack(fill=BOTH, padx=34, pady=4)
        Button(self.window, text="Export support bundle", command=self.export_support_bundle).pack(fill=BOTH, padx=34, pady=4)
        Button(self.window, text="Export full backup", command=self.export_full_backup).pack(fill=BOTH, padx=34, pady=4)
        Button(self.window, text="Restore full backup", command=self.restore_full_backup).pack(fill=BOTH, padx=34, pady=4)

    def log(self, message: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(line)
        except OSError:
            fallback = self.paths["logs"] / f"ndim-desktop-fallback-{os.getpid()}.log"
            try:
                with fallback.open("a", encoding="utf-8") as handle:
                    handle.write(line)
                self.log_path = fallback
            except OSError:
                pass

    def start_backend(self) -> None:
        def run() -> None:
            try:
                self.log("Backend thread entered")
                import uvicorn
                self.log("Imported uvicorn")
                from app.main import app
                self.log("Imported FastAPI app")

                logging.basicConfig(
                    filename=self.log_path,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                )
                self.log("Configuring uvicorn with log_config=None")
                config = uvicorn.Config(
                    app,
                    host=HOST,
                    port=self.port,
                    log_level="info",
                    access_log=False,
                    log_config=None,
                )
                self.server = uvicorn.Server(config)
                self.log(f"Starting backend at {self.url}")
                self.server.run()
                self.log("Backend server stopped")
            except Exception as exc:  # pragma: no cover - launcher safety net
                self.log(f"Backend failed: {exc}")
                self.status.set(f"Backend failed: {exc}")
                messagebox.showerror(APP_TITLE, f"NDIM backend failed to start.\n\n{exc}\n\nLog: {self.log_path}")

        self.log(f"Scheduling backend start at {self.url}")
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
        self.window.after(350, self.poll_backend)

    def poll_backend(self) -> None:
        try:
            with urllib.request.urlopen(f"http://{HOST}:{self.port}/api/status", timeout=0.5) as response:
                if response.status == 200:
                    self.status.set("NDIM Engine is running locally.")
                    self.open_app_button.configure(state=NORMAL)
                    if not self.opened:
                        self.open_app()
                    return
        except Exception:
            pass
        self.window.after(450, self.poll_backend)

    def open_app(self) -> None:
        self.opened = True
        webbrowser.open(self.url)

    def health_check(self) -> None:
        try:
            with urllib.request.urlopen(f"http://{HOST}:{self.port}/health", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            warnings = payload.get("warnings") or []
            detail = "NDIM Engine is offline-ready on this computer."
            if warnings:
                detail += "\n\nAttention:\n" + "\n".join(f"- {item}" for item in warnings)
            messagebox.showinfo(APP_TITLE, detail)
        except Exception as exc:
            messagebox.showwarning(APP_TITLE, f"NDIM Engine is still starting or needs attention.\n\n{exc}")

    def export_support_bundle(self) -> None:
        bundle = self.paths["support"] / f"ndim-support-{time.strftime('%Y%m%dT%H%M%S')}.zip"
        diagnostics = {
            "app": APP_TITLE,
            "url": self.url,
            "data_dir": str(self.paths["data"]),
            "resource_root": str(self.root_dir),
            "python": sys.version,
            "platform": sys.platform,
        }
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("diagnostics.json", json.dumps(diagnostics, indent=2))
            if self.log_path.exists():
                zf.write(self.log_path, "logs/ndim-desktop.log")
        messagebox.showinfo(APP_TITLE, f"Support bundle created:\n{bundle}")

    def export_full_backup(self) -> None:
        try:
            from app.storage import make_full_backup

            bundle = make_full_backup()
            messagebox.showinfo(APP_TITLE, f"Verified full local backup created:\n{bundle}")
        except Exception as exc:
            self.log(f"Full backup failed: {exc}")
            messagebox.showerror(APP_TITLE, f"Full backup could not be created.\n\n{exc}")

    def restore_full_backup(self) -> None:
        backup = filedialog.askopenfilename(title="Select NDIM backup", filetypes=[("Zip files", "*.zip")])
        if not backup:
            return
        if not messagebox.askyesno(
            APP_TITLE,
            "Restore this backup? NDIM will first verify the backup manifest and file hashes, then replace local data files.",
        ):
            return
        self.stop_server()
        try:
            from app.storage import restore_backup_archive

            result = restore_backup_archive(Path(backup))
            restored = result.get("restored_files", 0)
            messagebox.showinfo(APP_TITLE, f"Backup verified and restored ({restored} files). Restarting NDIM Engine.")
            self.start_backend()
        except Exception as exc:
            self.log(f"Backup restore failed: {exc}")
            messagebox.showerror(APP_TITLE, f"Backup restore stopped before changing data.\n\n{exc}")
            self.start_backend()

    def stop_server(self) -> None:
        if self.server is not None:
            self.server.should_exit = True
            time.sleep(0.5)

    def shutdown(self) -> None:
        self.stop_server()
        self.window.destroy()

    def run(self) -> None:
        self.start_backend()
        self.window.mainloop()


def main() -> None:
    DesktopApp().run()


if __name__ == "__main__":
    main()
