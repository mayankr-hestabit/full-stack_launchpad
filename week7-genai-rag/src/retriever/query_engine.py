from pathlib import Path
import json

import faiss
import numpy as np

from embeddings.embedder import Embedder


VECTORSTORE_DIR = Path(__file__).resolve().parents[1] / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


class QueryEngine:
    def __init__(self):
        print("Loading FAISS index...")

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            self.metadata = json.load(file)

        self.embedder = Embedder()

        print("Query engine ready.")


    def search(self, query, top_k=5):
        """
        Retrieves the most semantically relevant
        chunks for a natural-language query.
        """

        query_embedding = self.embedder.embed_text(query)

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            chunk = self.metadata[index]

            results.append({
                "score": float(score),
                "chunk": chunk
            })

        return results


if __name__ == "__main__":

    engine = QueryEngine()

    query = input(
        "\nEnter your question: "
    )

    results = engine.search(
        query=query,
        top_k=3
    )

    print("\nRetrieved Results:")

    for rank, result in enumerate(
        results,
        start=1
    ):

        chunk = result["chunk"]

        print(
            "\n===================================="
        )

        print(
            f"Rank: {rank}"
        )

        print(
            f"Similarity Score: "
            f"{result['score']:.4f}"
        )

        print(
            f"Source: {chunk['source']}"
        )

        print(
            f"Page: {chunk['page_number']}"
        )

        print(
            f"Chunk ID: {chunk['chunk_id']}"
        )

        print(
            f"Text: {chunk['text']}"
        )