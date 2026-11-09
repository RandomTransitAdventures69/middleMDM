#!/usr/bin/env python3
"""Tkinter setup and launcher for the middleMDM server."""
import os
import queue
import secrets
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk
except ImportError as exc:
    raise SystemExit(
        "Tkinter is required. Install your Python distribution's Tk support and retry."
    ) from exc


ROOT_DIR = Path(__file__).resolve().parent
SERVER_DIR = ROOT_DIR / "server"
SERVER_URL = "http://127.0.0.1:5001/"


def parse_env(text):
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.startswith("export "):
            key = key[7:].strip()
        values[key] = value.strip().strip("'\"")
    return values


def is_strong_secret(value):
    known_weak = {
        "change-me-in-production",
        "change-this-to-a-random-secret-key-in-production",
        "dev-enrollment-secret-change-me",
        "test-secret-key",
        "test-enrollment-secret",
    }
    return (
        len(value) >= 32
        and len(set(value)) >= 16
        and value == value.strip()
        and value.lower() not in known_weak
        and not value.lower().startswith(("change-", "replace-with", "your-"))
    )


def configure_local_env():
    """Create a development env file without replacing existing settings."""
    env_path = SERVER_DIR / ".env"
    template_path = SERVER_DIR / ".env.example"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    elif template_path.exists():
        lines = template_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = ["# middleMDM local server configuration"]

    values = parse_env("\n".join(lines))
    secret_key = values.get("SECRET_KEY", "")
    enrollment_secret = values.get("ENROLLMENT_SECRET", "")
    if not is_strong_secret(secret_key):
        secret_key = secrets.token_urlsafe(48)
    if not is_strong_secret(enrollment_secret) or enrollment_secret == secret_key:
        enrollment_secret = secrets.token_urlsafe(48)

    updates = {
        "FLASK_ENV": "development",
        "SECRET_KEY": secret_key,
        "HOST": "127.0.0.1",
        "PORT": values.get("PORT", "5001"),
        "ENROLLMENT_SECRET": enrollment_secret,
    }

    output = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            output.append(line)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key.startswith("export "):
            key = key[7:].strip()
        if key in updates:
            output.append(f"{key}={updates.pop(key)}")
        else:
            output.append(line)
    for key, value in updates.items():
        output.append(f"{key}={value}")

    env_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    if os.name != "nt":
        env_path.chmod(0o600)
    return env_path


class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("middleMDM Setup")
        self.root.geometry("720x560")
        self.root.minsize(620, 460)
        self.events = queue.Queue()
        self.task_running = False
        self.server_process = None

        container = ttk.Frame(root, padding=18)
        container.pack(fill="both", expand=True)
        ttk.Label(
            container,
            text="middleMDM Server Setup",
            font=("TkDefaultFont", 18, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            container,
            text=(
                "Prepare a local development server, create its administrator, "
                "and open the dashboard."
            ),
            wraplength=670,
        ).pack(anchor="w", pady=(5, 14))

        self.status = tk.StringVar(value="Ready")
        ttk.Label(container, textvariable=self.status).pack(anchor="w", pady=(0, 10))

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(0, 12))
        self.prepare_button = ttk.Button(
            controls, text="Prepare configuration", command=self.prepare
        )
        self.prepare_button.pack(side="left", padx=(0, 6))
        self.install_button = ttk.Button(
            controls, text="Install dependencies", command=self.install_dependencies
        )
        self.install_button.pack(side="left", padx=6)
        self.database_button = ttk.Button(
            controls, text="Initialize database", command=self.initialize_database
        )
        self.database_button.pack(side="left", padx=6)

        server_controls = ttk.Frame(container)
        server_controls.pack(fill="x", pady=(0, 12))
        self.start_button = ttk.Button(
            server_controls, text="Start server", command=self.start_server
        )
        self.start_button.pack(side="left", padx=(0, 6))
        self.stop_button = ttk.Button(
            server_controls, text="Stop server", command=self.stop_server, state="disabled"
        )
        self.stop_button.pack(side="left", padx=6)
        ttk.Button(
            server_controls, text="Open dashboard", command=self.open_dashboard
        ).pack(side="left", padx=6)

        ttk.Label(container, text="Activity").pack(anchor="w")
        log_frame = ttk.Frame(container)
        log_frame.pack(fill="both", expand=True, pady=(5, 0))
        self.log = tk.Text(log_frame, height=16, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.process_events)
        self.append_log(f"Project: {ROOT_DIR}")

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def run_task(self, label, action):
        if self.task_running:
            return
        self.task_running = True
        self.status.set(label)
        for button in (self.prepare_button, self.install_button, self.database_button):
            button.configure(state="disabled")

        def worker():
            try:
                action()
            except Exception as exc:
                self.events.put(("log", f"ERROR: {exc}"))
                self.events.put(("status", "Task failed"))
            else:
                self.events.put(("status", f"{label} complete"))
                self.events.put(("log", f"{label} complete."))
            finally:
                self.events.put(("task_done", None))

        threading.Thread(target=worker, daemon=True).start()

    def prepare(self):
        def action():
            env_path = configure_local_env()
            self.events.put(("log", f"Local configuration ready: {env_path}"))
            self.events.put(("log", "Secrets were generated or preserved; values are not displayed."))

        self.run_task("Preparing configuration", action)

    def install_dependencies(self):
        def action():
            configure_local_env()
            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(SERVER_DIR / "requirements.txt"),
            ]
            self.events.put(("log", "Installing server Python dependencies..."))
            result = subprocess.run(
                command,
                cwd=SERVER_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                self.events.put(("log", result.stdout))
            if result.stderr:
                self.events.put(("log", result.stderr))
            if result.returncode:
                raise RuntimeError(f"pip exited with status {result.returncode}")

        self.run_task("Installing dependencies", action)

    def initialize_database(self):
        password = simpledialog.askstring(
            "Initial administrator",
            "Set an initial admin password (at least 12 characters):",
            show="*",
            parent=self.root,
        )
        if password is None:
            return
        confirmation = simpledialog.askstring(
            "Confirm password",
            "Enter the admin password again:",
            show="*",
            parent=self.root,
        )
        if confirmation is None:
            return
        if len(password) < 12:
            messagebox.showerror("Password too short", "Use at least 12 characters.")
            return
        if password != confirmation:
            messagebox.showerror("Passwords do not match", "Enter matching passwords.")
            return

        def action():
            configure_local_env()
            env = os.environ.copy()
            env["FLASK_ENV"] = "development"
            command = [
                sys.executable,
                "-m",
                "flask",
                "--app",
                "run",
                "init-db",
                "--admin-password-stdin",
            ]
            result = subprocess.run(
                command,
                cwd=SERVER_DIR,
                env=env,
                input=f"{password}\n{password}\n",
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                self.events.put(("log", result.stdout))
            if result.stderr:
                self.events.put(("log", result.stderr))
            if result.returncode:
                raise RuntimeError(f"Database initialization exited with status {result.returncode}")

        self.run_task("Initializing database", action)

    def start_server(self):
        if self.task_running:
            return
        if self.server_process and self.server_process.poll() is None:
            self.status.set("Server is already running")
            return
        try:
            env_path = configure_local_env()
            env = os.environ.copy()
            env.update({"FLASK_ENV": "development", "HOST": "127.0.0.1", "PORT": "5001"})
            self.server_process = subprocess.Popen(
                [sys.executable, "run.py"],
                cwd=SERVER_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except (OSError, RuntimeError) as exc:
            messagebox.showerror("Could not start server", str(exc))
            return

        self.status.set("Starting local server...")
        self.stop_button.configure(state="normal")
        self.events.put(("log", f"Using configuration: {env_path}"))
        self.events.put(("log", f"Starting server at {SERVER_URL}"))
        threading.Thread(
            target=self.read_server_output,
            args=(self.server_process,),
            daemon=True,
        ).start()
        threading.Thread(
            target=self.wait_until_ready,
            args=(self.server_process,),
            daemon=True,
        ).start()

    def read_server_output(self, process):
        if process.stdout:
            for line in process.stdout:
                self.events.put(("log", line))
        return_code = process.wait()
        self.events.put(("server_exit", return_code))

    def wait_until_ready(self, process):
        for _ in range(40):
            if process.poll() is not None:
                return
            try:
                with socket.create_connection(("127.0.0.1", 5001), timeout=0.25):
                    self.events.put(("server_ready", None))
                    return
            except OSError:
                time.sleep(0.25)
        self.events.put(("log", "Server did not become ready; check the output above."))

    def stop_server(self):
        process = self.server_process
        if not process or process.poll() is not None:
            self.status.set("Server is stopped")
            self.stop_button.configure(state="disabled")
            return
        process.terminate()
        self.status.set("Stopping server...")

    def open_dashboard(self):
        webbrowser.open(SERVER_URL)

    def process_events(self):
        while True:
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self.append_log(value)
            elif kind == "status":
                self.status.set(value)
            elif kind == "task_done":
                self.task_running = False
                for button in (self.prepare_button, self.install_button, self.database_button):
                    button.configure(state="normal")
            elif kind == "server_ready":
                self.status.set("Server is running")
                webbrowser.open(SERVER_URL)
            elif kind == "server_exit":
                self.status.set(f"Server stopped (exit code {value})")
                self.stop_button.configure(state="disabled")
        self.root.after(100, self.process_events)

    def close(self):
        process = self.server_process
        if process and process.poll() is None:
            process.terminate()
        self.root.destroy()


def main():
    root = tk.Tk()
    SetupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
