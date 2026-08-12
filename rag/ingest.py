from pathlib import Path
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from database.chroma import get_database


KNOWLEDGE_DIR = Path("knowledge")


def file_hash(path):
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def load_documents():
    documents = []

    for file in KNOWLEDGE_DIR.rglob("*"):

        if file.suffix.lower() not in (
            ".md",
            ".txt",
        ):
            continue

        content = file.read_text(
            encoding="utf-8"
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file),
                    "file_hash": file_hash(file),
                },
            )
        )

    return documents


def main():

    print("[1] Loading documents...")

    documents = load_documents()

    print(
        f"[2] Loaded "
        f"{len(documents)} documents"
    )

    if not documents:
        print("[!] No documents found.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"[3] Created "
        f"{len(chunks)} chunks"
    )

    print(
        "[4] Connecting to ChromaDB..."
    )

    db = get_database()

    existing_hashes = set()

    existing = db.get(
        include=["metadatas"]
    )

    for metadata in existing["metadatas"]:

        if not metadata:
            continue

        file_hash_value = metadata.get(
            "file_hash"
        )

        if file_hash_value:
            existing_hashes.add(
                file_hash_value
            )

    new_chunks = []

    for chunk in chunks:

        file_hash_value = chunk.metadata.get(
            "file_hash"
        )

        if file_hash_value not in existing_hashes:
            new_chunks.append(chunk)

    if not new_chunks:

        print(
            "[5] No new documents to index."
        )

        print(
            f"Total vectors: "
            f"{db._collection.count()}"
        )

        return

    print(
        f"[5] New chunks: "
        f"{len(new_chunks)}"
    )

    db.add_documents(
        new_chunks
    )

    print(
        "[6] Documents added successfully."
    )

    print(
        f"Total vectors: "
        f"{db._collection.count()}"
    )


if __name__ == "__main__":
    main()