import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent

INDEX_PATH = BASE_DIR / "memory.index"
METADATA_PATH = BASE_DIR / "memory_metadata.json"


class VectorMemory:
    """
    Semantic memory using embeddings + FAISS.

    Stores text as vectors and retrieves memories
    based on semantic similarity.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.model = SentenceTransformer(
            model_name
        )

        self.dimension = (
            self.model.get_embedding_dimension()
        )

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.memories = []

        self._load()


    def _embed(
        self,
        texts: list[str],
    ) -> np.ndarray:
        """
        Convert text into normalized embeddings.
        """

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.astype(
            "float32"
        )


    def add_memory(
        self,
        content: str,
        memory_type: str = "semantic",
    ):
        """
        Add one memory to FAISS.
        """

        embedding = self._embed(
            [content]
        )

        self.index.add(
            embedding
        )

        self.memories.append(
            {
                "content": content,
                "memory_type": memory_type,
            }
        )

        self._save()


    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Search for semantically similar memories.
        """

        if self.index.ntotal == 0:
            return []

        query_embedding = self._embed(
            [query]
        )

        k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                k,
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            memory = self.memories[
                index
            ]

            results.append(
                {
                    "content":
                        memory["content"],

                    "memory_type":
                        memory["memory_type"],

                    "score":
                        float(score),
                }
            )

        return results


    def _save(self):
        """
        Persist FAISS index and metadata.
        """

        faiss.write_index(
            self.index,
            str(INDEX_PATH),
        )

        with open(
            METADATA_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.memories,
                file,
                indent=2,
            )


    def _load(self):
        """
        Load previously stored vector memory.
        """

        if (
            INDEX_PATH.exists()
            and METADATA_PATH.exists()
        ):
            self.index = faiss.read_index(
                str(INDEX_PATH)
            )

            with open(
                METADATA_PATH,
                "r",
                encoding="utf-8",
            ) as file:
                self.memories = (
                    json.load(file)
                )


    def clear(self):
        """
        Remove all vector memories.
        """

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.memories = []

        if INDEX_PATH.exists():
            INDEX_PATH.unlink()

        if METADATA_PATH.exists():
            METADATA_PATH.unlink()