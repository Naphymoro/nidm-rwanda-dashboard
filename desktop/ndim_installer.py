from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_NAME = "NDIM Engine"


def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def default_install_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Programs" / APP_NAME
    return Path.home() / "AppData" / "Local" / "Programs" / APP_NAME


def ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def create_shortcut(target_exe: Path, shortcut_path: Path, working_dir: Path | None = None) -> None:
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    working_dir = working_dir or target_exe.parent
    script = "\n".join(
        [
            "$wsh = New-Object -ComObject WScript.Shell",
            f"$shortcut = $wsh.CreateShortcut({ps_quote(shortcut_path)})",
            f"$shortcut.TargetPath = {ps_quote(target_exe)}",
            f"$shortcut.WorkingDirectory = {ps_quote(working_dir)}",
            f"$shortcut.IconLocation = {ps_quote(str(target_exe) + ',0')}",
            "$shortcut.Description = 'NDIM Engine local research tool'",
            "$shortcut.Save()",
        ]
    )
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
        creationflags=creationflags,
    )


def start_menu_shortcut_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP_NAME / f"{APP_NAME}.lnk"
    return Path.home() / "Start Menu" / "Programs" / APP_NAME / f"{APP_NAME}.lnk"


class Installer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} Setup")
        self.geometry("640x420")
        self.minsize(560, 360)

        self.install_dir = tk.StringVar(value=str(default_install_dir()))
        self.status = tk.StringVar(value="Ready to install NDIM Engine locally.")
        self.launch_after_install = tk.BooleanVar(value=True)

        self.configure(bg="#f7f3eb")
        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f7f3eb")
        style.configure("TLabel", background="#f7f3eb", foreground="#231f1a", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)

        root = ttk.Frame(self, padding=28)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Install NDIM Engine", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text=(
                "This installs the local NDIM research tool on this computer. "
                "The app runs on localhost, stores data locally, and includes the stress-test corpus."
            ),
            wraplength=560,
        ).pack(anchor="w", pady=(10, 24))

        ttk.Label(root, text="Install location").pack(anchor="w")
        row = ttk.Frame(root)
        row.pack(fill="x", pady=(6, 18))
        ttk.Entry(row, textvariable=self.install_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=self.choose_folder).pack(side="left", padx=(10, 0))

        ttk.Checkbutton(
            root,
            text="Open NDIM Engine after installation",
            variable=self.launch_after_install,
        ).pack(anchor="w", pady=(0, 18))

        ttk.Label(root, textvariable=self.status, wraplength=560).pack(anchor="w", pady=(0, 18))

        actions = ttk.Frame(root)
        actions.pack(fill="x", side="bottom")
        ttk.Button(actions, text="Install", command=self.install).pack(side="right")
        ttk.Button(actions, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 10))

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(Path(self.install_dir.get()).parent))
        if selected:
            selected_path = Path(selected)
            self.install_dir.set(str(selected_path if selected_path.name == APP_NAME else selected_path / APP_NAME))

    def install(self) -> None:
        payload = resource_path("payload", "NDIM Engine Runtime")
        launcher = payload / "Launch NDIM Engine.cmd"
        if not launcher.exists():
            messagebox.showerror("Installer error", f"Missing bundled application launcher: {launcher}")
            return

        destination = Path(self.install_dir.get()).expanduser()
        try:
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(payload, destination)
            app_target = destination / "Launch NDIM Engine.cmd"

            notes = resource_path("PACKAGE_NOTES.md")
            if notes.exists():
                shutil.copy2(notes, destination / "PACKAGE_NOTES.md")

            create_shortcut(app_target, start_menu_shortcut_path(), destination)
            self.status.set(f"Installed to {destination}")

            if self.launch_after_install.get():
                subprocess.Popen([str(app_target)], cwd=str(destination), shell=True)

            messagebox.showinfo(
                "Installation complete",
                "NDIM Engine is installed. You can open it from the Start Menu or the install folder.",
            )
            self.destroy()
        except Exception as exc:  # pragma: no cover - GUI installer guardrail
            messagebox.showerror("Installation failed", str(exc))
            self.status.set("Installation failed. See the error dialog for details.")


def main() -> None:
    Installer().mainloop()


if __name__ == "__main__":
    main()
