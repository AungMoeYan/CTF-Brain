from models.llm import LLM


SYSTEM_PROMPT = """
You are an expert CTF player.

Give technically accurate cybersecurity
and Capture The Flag guidance.

Explain your reasoning clearly and
provide practical commands when appropriate.

When solving a challenge:
1. Identify the likely attack surface.
2. Explain the reasoning behind each step.
3. Prefer practical and verifiable commands.
4. Do not invent results that have not been observed.
"""


def main():

    llm = LLM(
        provider="bedrock",
        model="deepseek.v3-v1:0",
    )

    question = """
How would you enumerate SUID binaries
on a Linux machine during a CTF?
"""

    print("[+] Sending request to DeepSeek V3.2 through Bedrock...")

    answer = llm.generate(
        question,
        system=SYSTEM_PROMPT,
    )

    print("\n========== RESPONSE ==========\n")

    print(answer)

    print("\n===============================")


if __name__ == "__main__":
    main()
