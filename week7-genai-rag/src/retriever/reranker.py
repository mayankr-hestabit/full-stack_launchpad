from sentence_transformers import CrossEncoder

from retriever.hybrid_retriever import HybridRetriever


class Reranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        """
        Load a cross-encoder model for reranking.
        """

        print(
            f"Loading reranker model: {model_name}"
        )

        self.model = CrossEncoder(
            model_name
        )

        print(
            "Reranker model loaded successfully."
        )


    def rerank(
        self,
        query,
        candidates,
        top_k=5
    ):
        """
        Rerank hybrid retrieval candidates
        based on query-document relevance.
        """

        if not candidates:
            return []

        pairs = [
            (
                query,
                candidate["chunk"]["text"]
            )
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs
        )

        reranked_results = []

        for candidate, score in zip(
            candidates,
            scores
        ):

            result = candidate.copy()

            result[
                "reranker_score"
            ] = float(score)

            reranked_results.append(
                result
            )

        reranked_results = sorted(
            reranked_results,
            key=lambda item: item[
                "reranker_score"
            ],
            reverse=True
        )

        return reranked_results[:top_k]


if __name__ == "__main__":

    query = input(
        "\nEnter your question: "
    )

    filters = {
        "year": "2024",
        "type": "policy"
    }

    hybrid_retriever = HybridRetriever()

    hybrid_results = (
        hybrid_retriever.hybrid_search(
            query,
            top_k=5,
            filters=filters
        )
    )

    reranker = Reranker()

    final_results = reranker.rerank(
        query,
        hybrid_results,
        top_k=5
    )

    print(
        "\n========== RERANKED RESULTS =========="
    )

    print(
        "Filters:",
        filters
    )

    if not final_results:

        print(
            "\nNo results found."
        )

    else:

        for rank, result in enumerate(
            final_results,
            start=1
        ):

            print(
                f"\n========== RESULT {rank} =========="
            )

            print(
                "Reranker Score:",
                result["reranker_score"]
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
                "Chunk ID:",
                result["chunk"]["chunk_id"]
            )

            print(
                "\nText:"
            )

            print(
                result["chunk"]["text"]
            )