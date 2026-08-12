from langchain_chroma import Chroma

from rag.embeddings import get_embedding_model


DB_PATH = "./database/chroma"


def get_database():
    embeddings = get_embedding_model()

    db = Chroma(
        collection_name="ctf_knowledge",
        embedding_function=embeddings,
        persist_directory=DB_PATH,
    )

    return db