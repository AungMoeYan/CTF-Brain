from models.llm import LLM


SYSTEM_PROMPT = """
You are an expert CTF player.

Give technically accurate cybersecurity
and Capture The Flag guidance.

Explain your reasoning clearly and
provide practical commands when appropriate.
"""


def main():

    llm = LLM(
        provider="deepseek",
        model="deepseek-chat",
    )

    question = """
    How would you enumerate SUID binaries
    on a Linux machine during a CTF?
    """

    print("[+] Sending request to DeepSeek...")

    answer = llm.generate(
        question,
        system=SYSTEM_PROMPT,
    )

    print("\n========== RESPONSE ==========\n")

    print(answer)

    print("\n===============================")


if __name__ == "__main__":
    main()