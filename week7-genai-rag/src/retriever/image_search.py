from pathlib import Path
import json

import faiss
import numpy as np

from pipelines.image_ingest import ImageIngestor
from embeddings.clip_embedder import CLIPEmbedder


VECTORSTORE_DIR = (
    Path(__file__).resolve().parents[1]
    / "vectorstore"
)

IMAGE_INDEX_PATH = (
    VECTORSTORE_DIR
    / "image_index.faiss"
)

IMAGE_METADATA_PATH = (
    VECTORSTORE_DIR
    / "image_metadata.json"
)


class ImageSearchEngine:

    def __init__(self):
        """
        Prepare image ingestion and CLIP embedding.
        """

        self.ingestor = ImageIngestor()
        self.embedder = CLIPEmbedder()

        self.index = None
        self.metadata = []


    def build_index(self):
        """
        Process all images, create CLIP image
        embeddings and store them in FAISS.
        """

        print(
            "\nStarting image ingestion..."
        )

        image_records = (
            self.ingestor.ingest_images()
        )

        if not image_records:
            raise ValueError(
                "No images found in data/images."
            )

        print(
            f"\nImages ready for embedding: "
            f"{len(image_records)}"
        )

        embeddings = []

        for record in image_records:

            print(
                f"Embedding image: "
                f"{record['source']}"
            )

            embedding = (
                self.embedder.embed_image(
                    record["path"]
                )
            )

            embeddings.append(
                embedding
            )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        print(
            "\nImage embedding matrix shape:",
            embeddings.shape
        )

        dimension = embeddings.shape[1]

        self.index = (
            faiss.IndexFlatIP(
                dimension
            )
        )

        self.index.add(
            embeddings
        )

        self.metadata = image_records

        faiss.write_index(
            self.index,
            str(IMAGE_INDEX_PATH)
        )

        with open(
            IMAGE_METADATA_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.metadata,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\nImage FAISS index saved to: "
            f"{IMAGE_INDEX_PATH}"
        )

        print(
            f"Image metadata saved to: "
            f"{IMAGE_METADATA_PATH}"
        )


    def load_index(self):
        """
        Load an existing image FAISS index
        and its metadata.
        """

        if not IMAGE_INDEX_PATH.exists():
            raise FileNotFoundError(
                "Image index not found. "
                "Run build_index() first."
            )

        if not IMAGE_METADATA_PATH.exists():
            raise FileNotFoundError(
                "Image metadata not found. "
                "Run build_index() first."
            )

        self.index = faiss.read_index(
            str(IMAGE_INDEX_PATH)
        )

        with open(
            IMAGE_METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(
                file
            )

        print(
            "\nImage index loaded successfully."
        )


    def search_by_text(
        self,
        query,
        top_k=5
    ):
        """
        Search images using a text query.
        """

        if self.index is None:
            self.load_index()

        query_embedding = (
            self.embedder.embed_text(
                query
            )
        )

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        top_k = min(
            top_k,
            self.index.ntotal
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            record = self.metadata[
                index
            ]

            results.append({
                "score": float(
                    score
                ),
                "image": record
            })

        return results

    def search_by_image(
      self,
      image_path,
      top_k=5
    ):
      """
      Search stored images using another image.
      """

      if self.index is None:
          self.load_index()

      query_embedding = (
          self.embedder.embed_image(
              image_path
          )
      )

      query_embedding = np.asarray(
          [query_embedding],
          dtype="float32"
      )

      top_k = min(
          top_k,
          self.index.ntotal
      )

      scores, indices = (
          self.index.search(
              query_embedding,
              top_k
          )
      )

      results = []

      for score, index in zip(
          scores[0],
          indices[0]
      ):

          if index == -1:
              continue

          record = self.metadata[
              index
          ]

          results.append({
              "score": float(score),
              "image": record
          })

      return results


    def build_image_context(self, search_results):
      """
      Convert retrieved image results into
      clean textual context for RAG.
      """

      context_parts = []

      for rank, result in enumerate(
          search_results,
          start=1
      ):
          image = result["image"]

          part = f"""
    Source {rank}: {image["source"]}
    Similarity Score: {result["score"]:.4f}

    Caption:
    {image["caption"]}

    OCR Text:
    {image["ocr_text"]}
    """.strip()

          context_parts.append(part)

      return "\n\n--------------------\n\n".join(
          context_parts
      )


if __name__ == "__main__":

    engine = ImageSearchEngine()

    mode = input(
        "\nEnter mode "
        "(build/text/image): "
    ).strip().lower()

    if mode == "build":

        engine.build_index()

    elif mode == "text":

      query = input(
          "\nEnter text query: "
      ).strip()

      results = engine.search_by_text(
          query,
          top_k=5
      )

      print(
          "\n========== TEXT TO IMAGE SEARCH =========="
      )

      for rank, result in enumerate(
          results,
          start=1
      ):
          image = result["image"]

          print(
              f"\n========== RESULT {rank} =========="
          )

          print(
              "Similarity Score:",
              result["score"]
          )

          print(
              "Source:",
              image["source"]
          )

          print(
              "Caption:",
              image["caption"]
          )

      context = engine.build_image_context(
          results
      )

      print(
          "\n========== RAG CONTEXT =========="
      )

      print(context)


    elif mode == "image":

        image_path = input(
            "\nEnter query image path: "
        ).strip()

        results = engine.search_by_image(
            image_path,
            top_k=5
        )

        print(
            "\n========== IMAGE TO IMAGE SEARCH =========="
        )

        for rank, result in enumerate(
            results,
            start=1
        ):
            image = result["image"]

            print(
                f"\n========== RESULT {rank} =========="
            )

            print(
                "Similarity Score:",
                result["score"]
            )

            print(
                "Source:",
                image["source"]
            )

            print(
                "Caption:",
                image["caption"]
            )

    else:

        print(
            "Invalid mode. Use build, text or image."
        )