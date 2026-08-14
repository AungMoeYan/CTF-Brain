import re


FLAG_PATTERNS = [
    r"flag\{[^{}\n]+\}",
    r"FLAG\{[^{}\n]+\}",
    r"CTF\{[^{}\n]+\}",
    r"ctf\{[^{}\n]+\}",
    r"HTB\{[^{}\n]+\}",
    r"picoCTF\{[^{}\n]+\}",
]


def detect_flags(data):
    """
    Search arbitrary tool output for common CTF flag formats.
    """

    if data is None:
        return []

    text = str(data)

    found = []

    for pattern in FLAG_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        for match in matches:

            if match not in found:
                found.append(match)

    return found
