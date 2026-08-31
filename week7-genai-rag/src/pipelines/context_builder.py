import tiktoken

from retriever.hybrid_retriever import HybridRetriever
from retriever.reranker import Reranker


class ContextBuilder:

    def __init__(
        self,
        max_tokens=1800,
        similarity_threshold=0.85
    ):
        """
        max_tokens:
        Maximum number of tokens allowed
        in the final context.

        similarity_threshold:
        Used for simple duplicate detection.
        """

        self.max_tokens = max_tokens
        self.similarity_threshold = similarity_threshold

        self.encoding = tiktoken.get_encoding(
            "cl100k_base"
        )


    def count_tokens(self, text):
        """
        Count number of tokens in text.
        """

        return len(
            self.encoding.encode(text)
        )


    def normalize_text(self, text):
        """
        Normalize text for duplicate comparison.
        """

        return " ".join(
            text.lower().split()
        )


    def is_duplicate(
        self,
        text,
        selected_texts
    ):
        """
        Simple duplicate / overlap detection.

        If a large portion of the new chunk already
        appears in a selected chunk, consider it
        duplicate.
        """

        normalized_text = self.normalize_text(
            text
        )

        new_words = set(
            normalized_text.split()
        )

        if not new_words:
            return True

        for selected_text in selected_texts:

            normalized_selected = (
                self.normalize_text(
                    selected_text
                )
            )

            selected_words = set(
                normalized_selected.split()
            )

            common_words = (
                new_words
                .intersection(
                    selected_words
                )
            )

            similarity = (
                len(common_words)
                /
                len(new_words)
            )

            if (
                similarity
                >= self.similarity_threshold
            ):
                return True

        return False


    def build_context(
        self,
        results
    ):
        """
        Build final context from reranked results.

        Steps:
        1. Remove duplicate chunks.
        2. Respect token budget.
        3. Preserve source information.
        """

        selected_chunks = []

        selected_texts = []

        total_tokens = 0


        for result in results:

            chunk = result["chunk"]

            text = chunk["text"]

            # -------------------------
            # Deduplication
            # -------------------------

            if self.is_duplicate(
                text,
                selected_texts
            ):
                continue


            chunk_tokens = (
                self.count_tokens(
                    text
                )
            )


            # -------------------------
            # Context-size control
            # -------------------------

            if (
                total_tokens
                + chunk_tokens
                > self.max_tokens
            ):
                continue


            selected_chunks.append(
                result
            )

            selected_texts.append(
                text
            )

            total_tokens += (
                chunk_tokens
            )


        # -------------------------
        # Build final context text
        # -------------------------

        context_parts = []

        for rank, result in enumerate(
            selected_chunks,
            start=1
        ):

            chunk = result["chunk"]

            source = chunk.get(
                "source",
                "unknown"
            )

            page = chunk.get(
                "page_number"
            )

            chunk_id = chunk.get(
                "chunk_id"
            )

            header = (
                f"[Source {rank}] "
                f"File: {source}, "
                f"Page: {page}, "
                f"Chunk: {chunk_id}"
            )

            context_parts.append(
                header
            )

            context_parts.append(
                chunk["text"]
            )

            context_parts.append(
                ""
            )


        final_context = "\n".join(
            context_parts
        )


        return {
            "context": final_context,
            "chunks": selected_chunks,
            "total_tokens": total_tokens
        }


if __name__ == "__main__":

    query = input(
        "\nEnter your question: "
    )


    filters = {
        "year": "2024",
        "type": "policy"
    }


    # -------------------------
    # Step 1: Hybrid Retrieval
    # -------------------------

    hybrid_retriever = (
        HybridRetriever()
    )

    hybrid_results = (
        hybrid_retriever.hybrid_search(
            query,
            top_k=5,
            filters=filters
        )
    )


    # -------------------------
    # Step 2: Reranking
    # -------------------------

    reranker = Reranker()

    reranked_results = (
        reranker.rerank(
            query,
            hybrid_results,
            top_k=5
        )
    )


    # -------------------------
    # Step 3: Context Building
    # -------------------------

    context_builder = (
        ContextBuilder(
            max_tokens=1800,
            similarity_threshold=0.85
        )
    )


    context_data = (
        context_builder.build_context(
            reranked_results
        )
    )


    # -------------------------
    # Output
    # -------------------------

    print(
        "\n========== FINAL CONTEXT =========="
    )

    print(
        context_data["context"]
    )


    print(
        "\n========== CONTEXT STATS =========="
    )

    print(
        "Chunks selected:",
        len(
            context_data["chunks"]
        )
    )

    print(
        "Total tokens:",
        context_data[
            "total_tokens"
        ]
    )

    print(
        "Maximum allowed tokens:",
        context_builder.max_tokens
    )