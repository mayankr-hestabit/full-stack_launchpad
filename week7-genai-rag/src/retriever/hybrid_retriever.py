from pathlib import Path
import json
import re

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from embeddings.embedder import Embedder


VECTORSTORE_DIR = Path(__file__).resolve().parents[1] / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


class HybridRetriever:

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

        # Prepare the corpus for BM25 keyword retrieval
        self.tokenized_corpus = [
            self.tokenize(chunk["text"])
            for chunk in self.metadata
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_corpus
        )

        print("Hybrid retriever ready.")


    def tokenize(self, text):
        """
        Convert text into lowercase word tokens
        for BM25 keyword search.
        """

        text = text.lower()

        tokens = re.findall(
            r"\b\w+\b",
            text
        )

        return tokens


    def matches_filters(
        self,
        chunk,
        filters=None
    ):
        """
        Check whether a chunk satisfies
        the provided metadata filters.
        """

        if not filters:
            return True

        source = chunk.get(
            "source",
            ""
        ).lower()

        text = chunk.get(
            "text",
            ""
        ).lower()

        tags = [
            tag.lower()
            for tag in chunk.get(
                "tags",
                []
            )
        ]

        for key, value in filters.items():

            value = str(value).lower()

            if key == "year":

                if (
                    value not in source
                    and value not in text
                ):
                    return False


            elif key == "type":

                if (
                    value not in source
                    and value not in tags
                    and value not in text
                ):
                    return False


            elif key == "source":

                if value not in source:
                    return False


            elif key == "file_type":

                file_type = chunk.get(
                    "file_type",
                    ""
                ).lower()

                if value != file_type:
                    return False


        return True


    def semantic_search(
        self,
        query,
        top_k=5,
        filters=None
    ):
        """
        Semantic retrieval using
        BGE embeddings + FAISS.
        """

        query_embedding = (
            self.embedder.embed_text(
                query
            )
        )

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        # Retrieve more candidates first
        # because some results may fail filters
        candidate_k = min(
            max(
                top_k * 3,
                top_k
            ),
            self.index.ntotal
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                candidate_k
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            chunk = self.metadata[index]

            if not self.matches_filters(
                chunk,
                filters
            ):
                continue

            results.append({
                "index": int(index),
                "semantic_score": float(
                    score
                ),
                "chunk": chunk
            })

            if len(results) >= top_k:
                break

        return results


    def keyword_search(
        self,
        query,
        top_k=5,
        filters=None
    ):
        """
        Keyword retrieval using BM25.
        """

        tokenized_query = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = np.argsort(
            scores
        )[::-1]

        results = []

        for index in ranked_indices:

            chunk = self.metadata[index]

            if not self.matches_filters(
                chunk,
                filters
            ):
                continue

            results.append({
                "index": int(index),
                "bm25_score": float(
                    scores[index]
                ),
                "chunk": chunk
            })

            if len(results) >= top_k:
                break

        return results


    def hybrid_search(
        self,
        query,
        top_k=5,
        filters=None
    ):
        """
        Combine semantic and keyword results
        using Reciprocal Rank Fusion (RRF).
        """

        semantic_results = (
            self.semantic_search(
                query,
                top_k=top_k,
                filters=filters
            )
        )

        keyword_results = (
            self.keyword_search(
                query,
                top_k=top_k,
                filters=filters
            )
        )

        combined = {}

        # Common RRF constant
        rrf_k = 60


        # -------------------------
        # Semantic ranking
        # -------------------------

        for rank, result in enumerate(
            semantic_results,
            start=1
        ):

            index = result["index"]

            if index not in combined:

                combined[index] = {
                    "index": index,
                    "chunk": result["chunk"],
                    "rrf_score": 0,
                    "semantic_score": None,
                    "bm25_score": None
                }

            combined[index][
                "rrf_score"
            ] += (
                1 / (
                    rrf_k + rank
                )
            )

            combined[index][
                "semantic_score"
            ] = result[
                "semantic_score"
            ]


        # -------------------------
        # BM25 ranking
        # -------------------------

        for rank, result in enumerate(
            keyword_results,
            start=1
        ):

            index = result["index"]

            if index not in combined:

                combined[index] = {
                    "index": index,
                    "chunk": result["chunk"],
                    "rrf_score": 0,
                    "semantic_score": None,
                    "bm25_score": None
                }

            combined[index][
                "rrf_score"
            ] += (
                1 / (
                    rrf_k + rank
                )
            )

            combined[index][
                "bm25_score"
            ] = result[
                "bm25_score"
            ]


        # Sort by final RRF score
        final_results = sorted(
            combined.values(),
            key=lambda item: item[
                "rrf_score"
            ],
            reverse=True
        )

        return final_results[:top_k]


if __name__ == "__main__":

    retriever = HybridRetriever()

    query = input(
        "\nEnter your question: "
    )

    filters = {
        "year": "2024",
        "type": "policy"
    }

    results = retriever.hybrid_search(
        query,
        top_k=5,
        filters=filters
    )

    print(
        "\n========== HYBRID SEARCH =========="
    )

    print(
        "Filters:",
        filters
    )

    if not results:

        print(
            "\nNo results matched the query "
            "and metadata filters."
        )

    else:

        for rank, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\n========== RESULT {rank} =========="
            )

            print(
                "RRF Score:",
                result["rrf_score"]
            )

            print(
                "Semantic Score:",
                result["semantic_score"]
            )

            print(
                "BM25 Score:",
                result["bm25_score"]
            )

            print(
                "Source:",
                result["chunk"]["source"]
            )

            print(
                "File Type:",
                result["chunk"]["file_type"]
            )

            print(
                "Page Number:",
                result["chunk"]["page_number"]
            )

            print(
                "Chunk ID:",
                result["chunk"]["chunk_id"]
            )

            print(
                "Tags:",
                result["chunk"]["tags"]
            )

            print(
                "\nText:"
            )

            print(
                result["chunk"]["text"]
            )