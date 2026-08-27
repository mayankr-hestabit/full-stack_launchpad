from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        """
        Loads a local embedding model.

        BGE-small is lightweight and suitable
        for semantic retrieval.
        """

        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Embedding model loaded successfully.")


    def embed_text(self, text):
        """
        Converts a single text string
        into one embedding vector.
        """

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding


    def embed_documents(self, chunks):
        """
        Converts multiple document chunks
        into embedding vectors.

        Expected chunk structure:
        {
            "chunk_id": ...,
            "text": ...,
            "source": ...,
            ...
        }
        """

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings


if __name__ == "__main__":

    embedder = Embedder()

    sample_text = (
        "Employees are entitled to "
        "24 paid leave days per year."
    )

    embedding = embedder.embed_text(sample_text)

    print("\nEmbedding generated successfully.")

    print("Embedding dimension:", len(embedding))

    print(
        "First 10 values:",
        embedding[:10]
    )