from pathlib import Path

from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration


IMAGE_DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "images"
)


class ImageIngestor:

    def __init__(
        self,
        caption_model="Salesforce/blip-image-captioning-base"
    ):
        """
        Load the BLIP model used for image captioning.
        """

        print(
            f"Loading image captioning model: "
            f"{caption_model}"
        )

        self.processor = BlipProcessor.from_pretrained(
            caption_model
        )

        self.caption_model = (
            BlipForConditionalGeneration
            .from_pretrained(
                caption_model
            )
        )

        print(
            "Image captioning model loaded."
        )


    def extract_ocr_text(self, image):
        """
        Extract visible text from an image
        using Tesseract OCR.
        """

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()


    def generate_caption(self, image):
        """
        Generate a natural-language description
        of the image using BLIP.
        """

        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        output = self.caption_model.generate(
            **inputs,
            max_new_tokens=50
        )

        caption = self.processor.decode(
            output[0],
            skip_special_tokens=True
        )

        return caption.strip()


    def process_image(self, image_path):
        """
        Process one image and return
        OCR text, caption and metadata.
        """

        image_path = Path(image_path)

        image = Image.open(
            image_path
        ).convert("RGB")

        print(
            f"\nProcessing image: "
            f"{image_path.name}"
        )

        ocr_text = self.extract_ocr_text(
            image
        )

        caption = self.generate_caption(
            image
        )

        record = {
            "image_id": image_path.stem,
            "source": image_path.name,
            "file_type": image_path.suffix.lower(),
            "ocr_text": ocr_text,
            "caption": caption,
            "path": str(image_path)
        }

        return record


    def ingest_images(self):
        """
        Process all supported images
        from data/images.
        """

        supported_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp"
        }

        records = []

        for image_path in IMAGE_DATA_DIR.iterdir():

            if not image_path.is_file():
                continue

            if (
                image_path.suffix.lower()
                not in supported_extensions
            ):
                continue

            try:

                record = self.process_image(
                    image_path
                )

                records.append(
                    record
                )

            except Exception as error:

                print(
                    f"Failed to process "
                    f"{image_path.name}: {error}"
                )

        return records


if __name__ == "__main__":

    ingestor = ImageIngestor()

    image_records = (
        ingestor.ingest_images()
    )

    print(
        f"\nTotal images processed: "
        f"{len(image_records)}"
    )

    for record in image_records:

        print(
            "\n=============================="
        )

        print(
            "Image ID:",
            record["image_id"]
        )

        print(
            "Source:",
            record["source"]
        )

        print(
            "File Type:",
            record["file_type"]
        )

        print(
            "\nOCR Text:"
        )

        print(
            record["ocr_text"]
        )

        print(
            "\nGenerated Caption:"
        )

        print(
            record["caption"]
        )