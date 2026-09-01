from PIL import Image

import torch
from transformers import CLIPProcessor, CLIPModel


class CLIPEmbedder:

    def __init__(
        self,
        model_name="openai/clip-vit-base-patch32"
    ):
        """
        Load CLIP model and processor.
        """

        print(
            f"Loading CLIP model: {model_name}"
        )

        self.model = CLIPModel.from_pretrained(
            model_name
        )

        self.processor = CLIPProcessor.from_pretrained(
            model_name
        )

        self.model.eval()

        print(
            "CLIP model loaded successfully."
        )


    def embed_image(self, image):
      """
      Convert one image into a CLIP
      embedding vector.
      """

      if not isinstance(image, Image.Image):
          image = Image.open(
              image
          ).convert("RGB")

      inputs = self.processor(
          images=image,
          return_tensors="pt"
      )

      with torch.no_grad():

          vision_outputs = self.model.vision_model(
              pixel_values=inputs["pixel_values"]
          )

          pooled_output = (
              vision_outputs.pooler_output
          )

          embedding = (
              self.model.visual_projection(
                  pooled_output
              )
          )

      embedding = (
          embedding
          / embedding.norm(
              dim=-1,
              keepdim=True
          )
      )

      return (
          embedding
          .squeeze(0)
          .cpu()
          .numpy()
      )


    def embed_text(self, text):
      """
      Convert text into a CLIP
      embedding vector.
      """

      inputs = self.processor(
          text=[text],
          return_tensors="pt",
          padding=True
      )

      with torch.no_grad():

          text_outputs = self.model.text_model(
              input_ids=inputs["input_ids"],
              attention_mask=inputs["attention_mask"]
          )

          pooled_output = (
              text_outputs.pooler_output
          )

          embedding = (
              self.model.text_projection(
                  pooled_output
              )
          )

      embedding = (
          embedding
          / embedding.norm(
              dim=-1,
              keepdim=True
          )
      )

      return (
          embedding
          .squeeze(0)
          .cpu()
          .numpy()
      )


if __name__ == "__main__":

    embedder = CLIPEmbedder()

    image_path = (
        "data/images/"
        "loan_approval_process.png"
    )

    image_embedding = (
        embedder.embed_image(
            image_path
        )
    )

    text_embedding = (
        embedder.embed_text(
            "loan approval process"
        )
    )

    print(
        "\nImage embedding dimension:",
        len(image_embedding)
    )

    print(
        "Text embedding dimension:",
        len(text_embedding)
    )

    print(
        "\nFirst 10 image values:",
        image_embedding[:10]
    )

    print(
        "\nFirst 10 text values:",
        text_embedding[:10]
    )