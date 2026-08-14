from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


TIMEOUT = 5

USER_AGENT = "CTF-Brain/1.0 (authorized-security-testing)"

MAX_PAGES = 10


def request(url):
    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=True,
        )

        return response, None

    except requests.RequestException as error:
        return None, str(error)


def normalize_url(url):
    parsed = urlparse(url)

    return parsed._replace(
        fragment=""
    ).geturl().rstrip("/")


def same_host(base_url, target_url):
    base = urlparse(base_url)
    target = urlparse(target_url)

    return (
        target.scheme in (
            "http",
            "https",
        )
        and target.netloc == base.netloc
    )


def extract_links(
    response,
    base_url,
):
    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    links = set()

    for tag in soup.find_all(
        "a",
        href=True,
    ):
        absolute = urljoin(
            base_url,
            tag["href"],
        )

        absolute = normalize_url(
            absolute
        )

        if same_host(
            base_url,
            absolute,
        ):
            links.add(absolute)

    return sorted(links)


def extract_forms(
    response,
    base_url,
):
    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    forms = []

    for form in soup.find_all(
        "form"
    ):
        action = form.get(
            "action",
            "",
        )

        method = form.get(
            "method",
            "GET",
        ).upper()

        action = urljoin(
            base_url,
            action,
        )

        inputs = []

        for element in form.find_all(
            ["input", "textarea", "select"]
        ):
            inputs.append(
                {
                    "name": element.get(
                        "name"
                    ),
                    "type": element.get(
                        "type",
                        element.name,
                    ),
                    "value": element.get(
                        "value",
                        "",
                    ),
                }
            )

        forms.append(
            {
                "action": action,
                "method": method,
                "inputs": inputs,
            }
        )

    return forms


def extract_scripts(
    response,
    base_url,
):
    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    scripts = []

    for script in soup.find_all(
        "script",
        src=True,
    ):
        scripts.append(
            urljoin(
                base_url,
                script["src"],
            )
        )

    return scripts


def crawl(start_url):
    start_url = normalize_url(
        start_url
    )

    queue = deque(
        [start_url]
    )

    visited = set()

    pages = []

    while queue and len(pages) < MAX_PAGES:

        current = queue.popleft()

        current = normalize_url(
            current
        )

        if current in visited:
            continue

        visited.add(current)

        response, error = request(
            current
        )

        if error:
            pages.append(
                {
                    "url": current,
                    "error": error,
                }
            )

            continue

        title = ""

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        links = extract_links(
            response,
            start_url,
        )

        forms = extract_forms(
            response,
            current,
        )

        scripts = extract_scripts(
            response,
            current,
        )

        page = {
            "url": current,
            "final_url": response.url,
            "status": response.status_code,
            "title": title,
            "content_type": response.headers.get(
                "Content-Type",
                "",
            ),
            "content_length": len(
                response.content
            ),
            "links": links,
            "forms": forms,
            "scripts": scripts,
        }

        pages.append(page)

        for link in links:

            if link not in visited:
                queue.append(link)

    return {
        "tool": "web_crawl",
        "start_url": start_url,
        "pages_crawled": len(pages),
        "pages": pages,
    }


def main():
    import json
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python -m tools.web_crawl <URL>"
        )
        return

    result = crawl(
        sys.argv[1]
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
