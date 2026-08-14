import json
import time
import re

from models.llm import LLM
from rag.search import search

from tools.router import execute_tool

from agent.state import CTFState
from agent.recon import ReconStrategy


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_PROVIDER = "bedrock"
MODEL_NAME = "deepseek.v3.2"


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are CTF Brain.

You are an expert Capture The Flag
and authorized security-lab assistant.

Your job is to investigate CTF targets,
use available tools when necessary,
reason over tool results, and ultimately
help identify flags.

Only operate against authorized CTF
targets and security labs.

AVAILABLE TOOLS:

1. nmap

Arguments:
{
    "target": "IP or hostname",
    "ports": "optional ports"
}

2. http

Arguments:
{
    "url": "http://target"
}

3. web_enum

Arguments:
{
    "url": "http://target"
}

4. web_crawl

Arguments:
{
    "url": "http://target"
}

Purpose:
Crawl the target website, follow discovered
same-host links, and collect pages, links,
forms, and scripts.

Use web_crawl when web_enum has discovered
interesting links or when deeper website
mapping is useful.

5. web_discovery

Arguments:
{
    "url": "http://target"
}

6. web_params

Arguments:
{
    "mode": "discover|test|api",
    "url": "http://target"
}

7. shell

Arguments:
{
    "command": "command"
}


DECISION FORMAT:

For a tool action:

{
    "decision": "tool",
    "tool": "nmap",
    "arguments": {
        "target": "127.0.0.1",
        "ports": "22"
    }
}

For a final answer:

{
    "decision": "final",
    "answer": "your answer"
}


RULES:

1. Analyze the current state.

2. Use RAG knowledge when relevant.

3. Use tools when actual target information
   is required.

4. Never claim that a command was executed
   unless a tool result confirms it.

5. Prefer one useful tool action at a time.

6. Do not repeat an action already performed
   unless new information justifies it.

7. When HTTP is discovered, use web_enum
   to understand the initial application.

8. If web_enum discovers interesting links,
   use web_crawl when deeper mapping is useful.

9. After crawling, inspect discovered pages,
   forms, scripts, and endpoints.

10. Use web_discovery when additional hidden
    paths may be useful.

11. Use web_params when parameters or APIs
    need investigation.

12. Use shell only when local command execution
    is appropriate for the authorized CTF.

13. If a flag is discovered, stop investigating.

14. Clearly distinguish observed results
    from reasoning.

15. Stay focused on the CTF objective.

16. Avoid repeating tools unnecessarily.

17. Prefer the smallest useful number of
    tool calls.

18. Return valid JSON for every decision.
"""


# ==========================================
# JSON PARSER
# ==========================================

def parse_json(text):

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)

        except json.JSONDecodeError:
            pass

    return None


# ==========================================
# FLAG DETECTOR
# ==========================================

def detect_flags(value):

    if not isinstance(value, str):
        return []

    patterns = [
        r"flag\{[^}]+\}",
        r"FLAG\{[^}]+\}",
        r"CTF\{[^}]+\}",
        r"picoCTF\{[^}]+\}",
    ]

    flags = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            value,
        )

        for match in matches:

            if match not in flags:
                flags.append(match)

    return flags


# ==========================================
# RAG CONTEXT
# ==========================================

def build_context(documents):

    if not documents:
        return "No relevant knowledge was found."

    parts = []

    for i, doc in enumerate(documents, 1):

        source = doc.metadata.get(
            "source",
            "unknown",
        )

        parts.append(
            f"""
========== SOURCE {i} ==========

Source:
{source}

Content:
{doc.page_content}
"""
        )

    return "\n".join(parts)


# ==========================================
# ASK AGENT
# ==========================================

def ask(question, state, recon):

    total_start = time.time()

    # ======================================
    # RAG
    # ======================================

    print(
        "\n[1] Searching knowledge base..."
    )

    search_start = time.time()

    documents = search(
        question,
        k=3,
    )

    search_time = (
        time.time()
        - search_start
    )

    print(
        f"[2] Search completed in "
        f"{search_time:.2f}s"
    )

    context = build_context(
        documents
    )

    # ======================================
    # AGENT LOOP
    # ======================================

    max_steps = 8

    for step in range(1, max_steps + 1):

        state_json = json.dumps(
            state.summary(),
            indent=2,
        )

        strategy = recon.prompt_context()

        prompt = f"""
USER QUESTION:

{question}


========================================

RETRIEVED KNOWLEDGE:

{context}


========================================

CURRENT CTF STATE:

{state_json}


========================================

{strategy}


========================================

TASK:

Analyze the current situation.

Decide whether another tool action is
necessary.

Available tools:

- nmap
- http
- web_enum
- web_crawl
- web_discovery
- web_params
- shell

If a tool is required, return JSON:

{{
    "decision": "tool",
    "tool": "web_crawl",
    "arguments": {{
        "url": "http://127.0.0.1:8000"
    }}
}}

If no tool is required, return JSON:

{{
    "decision": "final",
    "answer": "your answer"
}}

Return ONLY valid JSON.
"""

        # ==================================
        # MODEL
        # ==================================

        print(
            f"\n[3.{step}] Asking DeepSeek..."
        )

        llm_start = time.time()

        llm = LLM(
            provider=MODEL_PROVIDER,
            model=MODEL_NAME,
        )

        response = llm.generate(
            prompt,
            system=SYSTEM_PROMPT,
        )

        llm_time = (
            time.time()
            - llm_start
        )

        print(
            f"[3.{step}] Model response "
            f"in {llm_time:.2f}s"
        )

        # ==================================
        # PARSE DECISION
        # ==================================

        decision = parse_json(response)

        if not decision:

            print(
                "[!] Invalid JSON from model."
            )

            print(
                "[!] Raw response:"
            )

            print(response)

            return response

        decision_type = decision.get(
            "decision"
        )

        print(
            f"[4.{step}] Decision: "
            f"{decision_type}"
        )

        # ==================================
        # FINAL ANSWER
        # ==================================

        if decision_type == "final":

            answer = decision.get(
                "answer",
                "",
            )

            flags = detect_flags(
                answer
            )

            for flag in flags:
                state.add_flag(flag)

            total_time = (
                time.time()
                - total_start
            )

            print(
                f"\n[5] Total time: "
                f"{total_time:.2f}s"
            )

            return answer

        # ==================================
        # TOOL DECISION
        # ==================================

        if decision_type != "tool":

            return (
                "Invalid agent decision."
            )

        tool = decision.get(
            "tool"
        )

        arguments = decision.get(
            "arguments",
            {},
        )

        print(
            f"[4.{step}] Tool: {tool}"
        )

        print(
            f"[4.{step}] Arguments: "
            f"{arguments}"
        )

        # ==================================
        # DUPLICATE PREVENTION
        # ==================================

        if state.action_already_done(
            tool,
            arguments,
        ):

            print(
                "[!] Duplicate action "
                "blocked."
            )

            context += """

The requested tool action has already
been performed.

Do NOT repeat it.

Use the existing state and results
to decide the next useful action.
"""

            continue

        # ==================================
        # EXECUTE TOOL
        # ==================================

        tool_start = time.time()

        try:

            result = execute_tool(
                tool,
                arguments,
            )

        except Exception as error:

            result = {
                "error": str(error),
            }

        tool_time = (
            time.time()
            - tool_start
        )

        print(
            f"[5.{step}] Tool completed "
            f"in {tool_time:.2f}s"
        )

        # ==================================
        # SAVE RESULT
        # ==================================

        state.process_result(
            tool,
            arguments,
            result,
        )

        serialized = json.dumps(
            result,
            indent=2,
            default=str,
        )

        # ==================================
        # FLAG DETECTION
        # ==================================

        flags = detect_flags(
            serialized
        )

        if flags:

            for flag in flags:
                state.add_flag(flag)

            print(
                "\n[+] FLAG FOUND!"
            )

            for flag in flags:

                print(
                    f"[+] {flag}"
                )

            return (
                "Flag discovered:\n\n"
                + "\n".join(flags)
                + "\n\nEvidence:\n"
                + serialized
            )

        # ==================================
        # ADD TOOL RESULT TO CONTEXT
        # ==================================

        context += f"""

========================================

NEW TOOL RESULT

Tool:
{tool}

Arguments:
{json.dumps(
    arguments,
    indent=2,
)}

Result:
{serialized}

========================================
"""

    # ======================================
    # MAX STEPS
    # ======================================

    return (
        "Investigation reached the "
        "maximum number of agent steps."
    )


# ==========================================
# MAIN
# ==========================================

def main():

    print(
        """
========================================
              CTF BRAIN
        RAG + DeepSeek + Tools
========================================

Provider:
Amazon Bedrock

Model:
DeepSeek V3.2

Tools:
- Nmap
- HTTP
- Web Enumeration
- Web Crawling
- Web Discovery
- Web Parameters
- Shell

Type 'exit' or 'quit' to leave.
"""
    )

    while True:

        question = input(
            "\nCTF Brain > "
        )

        if question.lower() in (
            "exit",
            "quit",
        ):
            break

        if not question.strip():
            continue

        state = CTFState()

        recon = ReconStrategy(
            state
        )

        try:

            answer = ask(
                question,
                state,
                recon,
            )

            print(
                "\n========== ANSWER ==========\n"
            )

            print(answer)

            print(
                "\n============================"
            )

        except Exception as error:

            print(
                f"\n[ERROR] {error}"
            )


if __name__ == "__main__":
    main()
