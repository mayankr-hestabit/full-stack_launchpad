from pathlib import Path
import json

import faiss
import numpy as np

from pipelines.ingest import ingest_raw_documents
from embeddings.embedder import Embedder


VECTORSTORE_DIR = Path(__file__).resolve().parent

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


def flatten_chunks(documents):
    """
    Converts this structure:

    [
        {
            "source": "...",
            "file_type": "...",
            "chunks": [...]
        }
    ]

    into one flat list of chunks.
    """

    all_chunks = []

    for document in documents:
        for chunk in document["chunks"]:
            all_chunks.append(chunk)

    return all_chunks


def build_faiss_index():
    """
    Complete pipeline:

    raw documents
        ↓
    ingestion
        ↓
    chunks + metadata
        ↓
    embeddings
        ↓
    FAISS index
        ↓
    index.faiss + metadata.json
    """

    print("Starting document ingestion...")

    documents = ingest_raw_documents()

    chunks = flatten_chunks(documents)

    if not chunks:
        raise ValueError(
            "No chunks found. Add documents to data/raw first."
        )

    print(
        f"\nTotal chunks ready for embedding: {len(chunks)}"
    )

    embedder = Embedder()

    embeddings = embedder.embed_documents(chunks)

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        f"Embedding matrix shape: {embeddings.shape}"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print(
        f"Vectors stored in FAISS: {index.ntotal}"
    )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nFAISS index saved to: {INDEX_PATH}"
    )

    print(
        f"Metadata saved to: {METADATA_PATH}"
    )


if __name__ == "__main__":
    build_faiss_index()