from urllib.parse import urljoin

import requests


TIMEOUT = 5

DEFAULT_WORDS = [
    "admin",
    "login",
    "dashboard",
    "api",
    "api/v1",
    "api/v2",
    "uploads",
    "upload",
    "files",
    "backup",
    "backups",
    "config",
    "dev",
    "test",
    "debug",
    "docs",
    "documentation",
    "swagger",
    "swagger-ui",
    "graphql",
    "robots.txt",
    "sitemap.xml",
    ".git/HEAD",
    ".env",
    "server-status",
]


USER_AGENT = (
    "CTF-Brain/1.0 "
    "(authorized-security-testing)"
)


def discover(url, words=None):
    url = url.rstrip("/") + "/"

    words = words or DEFAULT_WORDS

    results = []

    for word in words:

        target = urljoin(
            url,
            word,
        )

        try:
            response = requests.get(
                target,
                timeout=TIMEOUT,
                allow_redirects=False,
                headers={
                    "User-Agent": USER_AGENT
                },
            )

        except requests.RequestException:
            continue

        if response.status_code == 404:
            continue

        results.append(
            {
                "path": "/" + word.lstrip("/"),
                "url": target,
                "status": response.status_code,
                "length": len(
                    response.content
                ),
                "content_type": response.headers.get(
                    "Content-Type",
                    "",
                ),
                "location": response.headers.get(
                    "Location"
                ),
            }
        )

    return {
        "tool": "web_discovery",
        "url": url.rstrip("/"),
        "count": len(results),
        "results": results,
    }


def main():
    import json
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python -m tools.web_discovery <URL>"
        )
        sys.exit(1)

    print(
        json.dumps(
            discover(sys.argv[1]),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
