from tools.nmap import scan
from tools.http import request
from tools.shell import run
from tools.web_enum import enumerate_web
from tools.web_discovery import discover

from tools.web_params import (
    discover_parameters,
    test_parameters,
    enumerate_api,
)

from tools.web_crawl import crawl

def execute_tool(tool, arguments):

    # =========================
    # NMAP
    # =========================

    if tool == "nmap":

        return scan(
            arguments["target"],
            arguments.get("ports"),
        )

    # =========================
    # HTTP
    # =========================

    if tool == "http":

        return request(
            arguments["url"]
        )

    # =========================
    # SHELL
    # =========================

    if tool == "shell":

        return run(
            arguments["command"]
        )

    # =========================
    # WEB ENUMERATION
    # =========================

    if tool == "web_enum":

        return enumerate_web(
            arguments["url"]
        )

    # =========================
    # WEB DISCOVERY
    # =========================

    if tool == "web_discovery":

        return discover(
            arguments["url"]
        )

    # =========================
    # WEB PARAMETERS / API
    # =========================

    if tool == "web_params":

        mode = arguments.get(
            "mode",
            "discover",
        )

        url = arguments["url"]

        if mode == "discover":

            return discover_parameters(
                url
            )

        if mode == "test":

            return test_parameters(
                url
            )

        if mode == "api":

            return enumerate_api(
                url
            )

        raise ValueError(
            f"Unknown web_params mode: {mode}"
        )

    if tool == "web_crawl":
        return crawl(
            arguments["url"]
        )

    # =========================
    # UNKNOWN TOOL
    # =========================

    raise ValueError(
        f"Unknown tool: {tool}"
    )

