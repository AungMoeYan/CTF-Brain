import requests


def request(url, method="GET"):

    try:

        response = requests.request(
            method,
            url,
            timeout=10,
            allow_redirects=True,
        )

        return {
            "url": url,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text[:10000],
        }

    except requests.RequestException as error:

        return {
            "url": url,
            "error": str(error),
        }
