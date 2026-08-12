from database.chroma import get_database


def search(query, k=3):

    db = get_database()

    results = db.similarity_search(
        query,
        k=k,
    )

    return results


def main():

    print("=== CTF Brain RAG Search ===")

    while True:

        query = input("\nQuery > ")

        if query.lower() in ("exit", "quit"):
            break

        results = search(query)

        print("\n========== RESULTS ==========")

        for i, doc in enumerate(results, 1):

            print(f"\n[{i}]")
            print(doc.page_content)
            print(f"\nSource: {doc.metadata.get('source')}")

        print("\n=============================")


if __name__ == "__main__":
    main()