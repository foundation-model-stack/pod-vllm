import subprocess
import os


def load_environment_from_shell_script(shell_script_path):
    # Construct the shell command
    command = ["bash", "-c", f'source "{shell_script_path}" && env']

    # Execute the command
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),  # Pass the current environment
    )

    # Capture the output and errors
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        print(f"Error sourcing script: {stderr}")
        return

    # Parse and update os.environ
    for line in stdout.splitlines():
        key, _, value = line.partition("=")
        os.environ[key] = value
