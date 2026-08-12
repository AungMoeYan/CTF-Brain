import time

from models.llm import LLM
from rag.search import search


# ==========================================
# MODEL CONFIGURATION
# ==========================================

# Development:
MODEL_PROVIDER = "ollama"
MODEL_NAME = "qwen3:8b"

# Competition/cloud:
# MODEL_PROVIDER = "deepseek"
# MODEL_NAME = "deepseek-chat"


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are CTF Brain, an expert Capture The Flag
player and cybersecurity assistant.

Your primary goal is to help solve authorized
CTF challenges and security labs.

Use the retrieved knowledge as your primary
source when it is relevant.

Rules:

1. Analyze the challenge carefully.

2. Use the supplied knowledge when relevant.

3. If the knowledge is incomplete, combine it
   with your cybersecurity knowledge.

4. Explain why a technique or command is
   appropriate.

5. Prefer practical commands and examples.

6. Never claim that you executed a command
   unless a tool actually executed it.

7. Clearly distinguish retrieved information
   from your own reasoning.

8. Think like an experienced CTF player.

9. When multiple approaches are possible,
   compare them and recommend the most
   promising one.

10. Focus on authorized CTF environments,
    challenge machines, and security labs.
"""


# ==========================================
# CONTEXT BUILDER
# ==========================================

def build_context(documents):

    if not documents:
        return "No relevant knowledge was found."

    parts = []

    for i, doc in enumerate(documents, 1):

        source = doc.metadata.get(
            "source",
            "unknown"
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
# CTF QUESTION
# ==========================================

def ask(question):

    total_start = time.time()

    # ------------------------------
    # RAG SEARCH
    # ------------------------------

    print("\n[1] Searching knowledge base...")

    search_start = time.time()

    documents = search(
        question,
        k=3
    )

    search_time = time.time() - search_start

    print(
        f"[2] Search completed in "
        f"{search_time:.2f}s"
    )

    # ------------------------------
    # BUILD CONTEXT
    # ------------------------------

    context = build_context(
        documents
    )

    # ------------------------------
    # BUILD PROMPT
    # ------------------------------

    prompt = f"""
You are solving a CTF-related question.

Relevant knowledge:

{context}

================================

User question:

{question}

================================

Using the knowledge above and your own
cybersecurity reasoning, provide the best
practical answer.

If the retrieved knowledge does not fully
answer the question, say what is missing
and continue using your own knowledge.
"""

    # ------------------------------
    # MODEL
    # ------------------------------

    print(
        f"[3] Sending request to "
        f"{MODEL_PROVIDER}:{MODEL_NAME}..."
    )

    llm_start = time.time()

    llm = LLM(
        provider=MODEL_PROVIDER,
        model=MODEL_NAME
    )

    answer = llm.generate(
        prompt,
        system=SYSTEM_PROMPT
    )

    llm_time = time.time() - llm_start

    print(
        f"[4] Model completed in "
        f"{llm_time:.2f}s"
    )

    total_time = time.time() - total_start

    print(
        f"[5] Total time: "
        f"{total_time:.2f}s"
    )

    return answer


# ==========================================
# CLI
# ==========================================

def main():

    print("""
========================================
             CTF BRAIN
       RAG + LLM Prototype
========================================

Model:
Qwen3:8B / Ollama

Type 'exit' or 'quit' to leave.
""")

    while True:

        question = input(
            "\nCTF Brain > "
        )

        if question.lower() in (
            "exit",
            "quit"
        ):
            break

        if not question.strip():
            continue

        try:

            answer = ask(
                question
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