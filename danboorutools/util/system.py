import subprocess


def run_external_command(command: str) -> subprocess.CompletedProcess:
    """Run a subprocess command safely and return the output as a string."""
    try:
        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        printable_output = e.output.decode(errors="backslashreplace")
        raise RuntimeError(f"Command '{e.cmd}' exited with error (code {e.returncode}): {printable_output}") from e
    return output
