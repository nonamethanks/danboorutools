import subprocess


def run_external_command(command: str) -> subprocess.CompletedProcess[bytes]:
    """Run a subprocess command safely and return the output as a string."""
    try:
        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            shell=True,  # noqa: S602
        )
    except subprocess.CalledProcessError as e:
        printable_output = e.output.decode(errors="backslashreplace")
        raise RuntimeError(f"External command '{e.cmd}' exited with error (code {e.returncode}): {printable_output}") from e
    return output
