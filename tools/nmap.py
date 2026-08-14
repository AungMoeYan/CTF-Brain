import subprocess


def scan(target, ports=None):

    if ports:
        command = [
            "nmap",
            "-sV",
            "-Pn",
            "-p",
            ports,
            target,
        ]
    else:
        command = [
            "nmap",
            "-sV",
            "-Pn",
            target,
        ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
        )

        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:

        return {
            "command": " ".join(command),
            "returncode": -1,
            "stdout": "",
            "stderr": "Nmap scan timed out.",
        }
