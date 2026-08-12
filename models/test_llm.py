from models.llm import LLM


SYSTEM_PROMPT = """
You are a CTF cybersecurity assistant.

Give technically accurate answers.
Prefer practical Linux commands when appropriate.
"""


def main():
    llm = LLM(
        provider="ollama",
        model="qwen3:8b",
    )

    print("CTF Brain - Model Test")
    print("======================")

    question = input("\nQuestion > ")

    print("\n[+] Sending to Qwen3:8B...\n")

    answer = llm.generate(
        question,
        system=SYSTEM_PROMPT,
    )

    print("========== RESPONSE ==========\n")
    print(answer)
    print("\n==============================")


if __name__ == "__main__":
    main()