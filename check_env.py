# check_env.py
# This script confirms our virtual environment and key packages are installed and importable.

import sys  # Provides access to Python version and environment info.
import subprocess  # Lets us run shell commands (we'll use it to print package versions).
from typing import List

def run(cmd: List[str]) -> None:
    """
    Runs a shell command and prints its output.
    We accept a list (command + args) for safety and clarity.
    """
    # subprocess.run executes the command; capture_output=True grabs stdout/stderr as strings.
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Print a friendly label (the command itself) so the output is easy to read.
    print(f"$ {' '.join(cmd)}")
    # Print whatever the command returned on standard output (usually the useful info).
    print(result.stdout.strip())
    # If there's any error text, show it too (helps with debugging missing installs).
    if result.stderr.strip():
        print("[stderr]", result.stderr.strip())
    print("-" * 40)  # A divider line for readability.

if __name__ == "__main__":
    # Show the Python interpreter version; confirms venv is active if the path points to .venv.
    print("Python executable:", sys.executable)  # Absolute path of the Python binary in use.
    print("Python version:", sys.version.split()[0])  # The short version number (e.g., 3.12.5)
    print("-" * 40)

    # Print pip version to confirm package manager is available in this environment.
    run([sys.executable, "-m", "pip", "--version"])

    # Ask Django to report its version; proves the import works from our venv.
    run([sys.executable, "-m", "django", "--version"])

    # Optionally, show installed packages to confirm our requirements were applied.
    run([sys.executable, "-m", "pip", "freeze"])
