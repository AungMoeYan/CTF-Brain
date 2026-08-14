import subprocess


def run(command, timeout=30):

    try:

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[:10000],
            "stderr": result.stderr[:5000],
        }

    except subprocess.TimeoutExpired:

        return {
            "command": command,
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out.",
        }
