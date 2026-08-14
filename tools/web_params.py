import re
from urllib.parse import (
    urljoin,
    urlparse,
    parse_qs,
)

import requests


TIMEOUT = 5

USER_AGENT = "CTF-Brain/1.0 (authorized-security-testing)"


PARAMETER_NAMES = [
    "id",
    "user",
    "uid",
    "username",
    "page",
    "file",
    "path",
    "url",
    "uri",
    "redirect",
    "next",
    "return",
    "returnUrl",
    "target",
    "query",
    "search",
    "q",
    "cmd",
    "command",
    "action",
    "debug",
    "token",
]


def request(url, method="GET", **kwargs):
    headers = kwargs.pop("headers", {})

    headers.setdefault(
        "User-Agent",
        USER_AGENT,
    )

    kwargs.setdefault(
        "timeout",
        TIMEOUT,
    )

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs,
        )

        return response, None

    except requests.RequestException as error:
        return None, str(error)


def extract_urls(text, base_url):
    urls = set()

    patterns = [
        r'href=["\']([^"\']+)["\']',
        r'src=["\']([^"\']+)["\']',
        r'action=["\']([^"\']+)["\']',
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE,
        )

        for value in matches:

            absolute = urljoin(
                base_url,
                value,
            )

            parsed = urlparse(
                absolute
            )

            if parsed.scheme in (
                "http",
                "https",
            ):
                urls.add(
                    absolute
                )

    return sorted(urls)


def extract_parameters(url):
    parsed = urlparse(url)

    params = parse_qs(
        parsed.query,
        keep_blank_values=True,
    )

    return sorted(
        params.keys()
    )


def discover_parameters(url):
    response, error = request(url)

    if error:
        return {
            "success": False,
            "error": error,
        }

    urls = extract_urls(
        response.text,
        response.url,
    )

    discovered = {}

    for discovered_url in urls:

        params = extract_parameters(
            discovered_url
        )

        if params:
            discovered[
                discovered_url
            ] = params

    return {
        "success": True,
        "base_url": response.url,
        "parameters": discovered,
    }


def build_candidate_urls(
    url,
    parameters=None,
):
    parameters = (
        parameters
        or PARAMETER_NAMES
    )

    separator = (
        "&"
        if "?" in url
        else "?"
    )

    candidates = []

    for parameter in parameters:

        candidate = (
            f"{url}"
            f"{separator}"
            f"{parameter}=CTFTEST"
        )

        candidates.append(
            candidate
        )

    return candidates


def compare_responses(
    original,
    modified,
):
    original_text = original.text
    modified_text = modified.text

    return {
        "original_status": (
            original.status_code
        ),
        "modified_status": (
            modified.status_code
        ),
        "original_length": len(
            original.content
        ),
        "modified_length": len(
            modified.content
        ),
        "length_difference": (
            len(modified.content)
            - len(original.content)
        ),
        "status_changed": (
            original.status_code
            != modified.status_code
        ),
        "length_changed": (
            len(original.content)
            != len(modified.content)
        ),
        "redirect_changed": (
            original.url
            != modified.url
        ),
        "url_original": original.url,
        "url_modified": modified.url,
        "content_changed": (
            original_text
            != modified_text
        ),
    }


def test_parameters(
    url,
    parameters=None,
):
    original, error = request(url)

    if error:
        return {
            "success": False,
            "error": error,
        }

    candidates = build_candidate_urls(
        url,
        parameters,
    )

    results = []

    for candidate in candidates:

        response, error = request(
            candidate
        )

        if error:
            continue

        comparison = compare_responses(
            original,
            response,
        )

        comparison["parameter"] = (
            urlparse(candidate)
            .query
            .split("=")[0]
        )

        comparison["url"] = candidate

        results.append(
            comparison
        )

    return {
        "success": True,
        "url": url,
        "tested": len(results),
        "results": results,
    }


def enumerate_api(url):
    response, error = request(url)

    if error:
        return {
            "success": False,
            "error": error,
        }

    text = response.text

    candidates = set()

    patterns = [
        r'["\'](/api[^"\']*)',
        r'["\'](/v[0-9]+/[^"\']*)',
        r'["\'](/graphql[^"\']*)',
        r'["\'](/swagger[^"\']*)',
        r'["\'](/openapi[^"\']*)',
        r'["\'](/api-docs[^"\']*)',
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE,
        )

        for match in matches:

            candidates.add(
                urljoin(
                    response.url,
                    match,
                )
            )

    common_api_paths = [
        "/api",
        "/api/",
        "/api/v1",
        "/api/v1/",
        "/api/v2",
        "/api/v2/",
        "/graphql",
        "/swagger",
        "/swagger/",
        "/swagger-ui/",
        "/openapi.json",
        "/swagger.json",
        "/api-docs",
    ]

    for path in common_api_paths:

        candidates.add(
            urljoin(
                response.url,
                path,
            )
        )

    results = []

    for candidate in sorted(
        candidates
    ):

        result, error = request(
            candidate,
            allow_redirects=False,
        )

        if error:
            continue

        if result.status_code == 404:
            continue

        results.append(
            {
                "url": candidate,
                "status": result.status_code,
                "length": len(
                    result.content
                ),
                "content_type": (
                    result.headers.get(
                        "Content-Type",
                        "",
                    )
                ),
                "location": (
                    result.headers.get(
                        "Location"
                    )
                ),
            }
        )

    return {
        "success": True,
        "base_url": response.url,
        "count": len(results),
        "results": results,
    }


def main():
    import json
    import sys

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python -m tools.web_params "
            "<mode> <URL>"
        )

        print()
        print(
            "Modes:"
        )
        print(
            "  discover"
        )
        print(
            "  test"
        )
        print(
            "  api"
        )

        sys.exit(1)

    mode = sys.argv[1]
    url = sys.argv[2]

    if mode == "discover":

        result = discover_parameters(
            url
        )

    elif mode == "test":

        result = test_parameters(
            url
        )

    elif mode == "api":

        result = enumerate_api(
            url
        )

    else:

        print(
            f"Unknown mode: {mode}"
        )

        sys.exit(1)

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
