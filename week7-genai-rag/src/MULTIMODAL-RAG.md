# MULTIMODAL RAG

## 1. Overview

The Multimodal RAG module extends the existing text-based RAG system to support image-based knowledge.

Enterprise information may exist in:

- Infographics
- Dashboards
- Charts
- Screenshots
- Scanned documents
- Diagrams

The system can process images, extract information from them, generate multimodal embeddings, store them in FAISS, and retrieve relevant images using either text or image queries.

The current implementation supports:

- Image ingestion
- OCR text extraction
- Image captioning
- CLIP embeddings
- FAISS image indexing
- Text-to-image retrieval
- Image-to-image retrieval
- Image-to-text context generation


---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Pillow | Image loading |
| Tesseract OCR | Extract text from images |
| BLIP | Generate image captions |
| CLIP | Generate text and image embeddings |
| Hugging Face Transformers | Load BLIP and CLIP |
| PyTorch | Model inference |
| FAISS | Vector similarity search |
| NumPy | Vector processing |


---

## 3. Project Structure

```text
src/
│
├── data/
│   └── images/
│
├── pipelines/
│   └── image_ingest.py
│
├── embeddings/
│   └── clip_embedder.py
│
├── retriever/
│   └── image_search.py
│
├── vectorstore/
│   ├── image_index.faiss
│   └── image_metadata.json
│
└── MULTIMODAL-RAG.md
```


---

## 4. Image Ingestion

Image ingestion is handled by:

```text
pipelines/image_ingest.py
```

The pipeline reads images from:

```text
data/images/
```

Supported formats include:

```text
.png
.jpg
.jpeg
.webp
```

For every image, the system performs:

```text
Image
  │
  ├── Tesseract OCR
  │       ↓
  │   Extracted Text
  │
  └── BLIP
          ↓
      Image Caption
```


---

## 5. OCR with Tesseract

Tesseract OCR extracts visible text from images.

Example:

```text
EMPLOYEE LEAVE POLICY

Annual Leave
24 days per year

Sick Leave
12 days per year
```

Pipeline:

```text
Image
  ↓
Tesseract OCR
  ↓
Machine-readable Text
```

OCR is especially useful for:

- Policy images
- Reports
- Dashboards
- Screenshots
- Scanned documents

OCR output can sometimes contain noise when icons or graphical elements are interpreted as text.


---

## 6. BLIP Image Captioning

The model used for captioning is:

```text
Salesforce/blip-image-captioning-base
```

BLIP generates a short description of the image.

Example:

```text
Input:
loan_approval_process.png

Caption:
loan process diagram
```

OCR and BLIP have different roles:

```text
Tesseract → Extract visible words

BLIP → Describe the overall image
```


---

## 7. Image Metadata

For every image, the system stores metadata such as:

```json
{
    "image_id": "loan_approval_process",
    "source": "loan_approval_process.png",
    "file_type": ".png",
    "ocr_text": "LOAN APPROVAL PROCESS...",
    "caption": "loan process diagram",
    "path": "data/images/loan_approval_process.png"
}
```

This metadata allows the application to map a FAISS result back to the actual image and its extracted information.


---

## 8. CLIP Embeddings

CLIP is implemented in:

```text
embeddings/clip_embedder.py
```

The model used is:

```text
openai/clip-vit-base-patch32
```

CLIP can encode both text and images.

```text
Image
  ↓
CLIP Vision Encoder
  ↓
512-D Vector
```

and:

```text
Text
  ↓
CLIP Text Encoder
  ↓
512-D Vector
```

Both vectors exist in the same compatible embedding space.

This allows direct comparison between text and image representations.


---

## 9. Shared Embedding Space

For example:

```text
"loan approval process"
        ↓
CLIP Text Encoder
        ↓
512-D Text Vector
        │
        │ similarity
        ▼
512-D Image Vector
        ↑
CLIP Image Encoder
        ↑
loan_approval_process.png
```

If the text and image represent similar concepts, their vectors should have a higher similarity score.


---

## 10. Vector Normalization

Both text and image vectors are normalized.

```text
Vector
  ↓
Normalization
  ↓
Unit-length Vector
```

This allows FAISS inner-product similarity to behave similarly to cosine similarity.


---

## 11. FAISS Image Index

Image retrieval is implemented in:

```text
retriever/image_search.py
```

The FAISS index uses:

```python
faiss.IndexFlatIP(512)
```

The indexing pipeline is:

```text
Images
  ↓
Image Ingestion
  ↓
CLIP Image Embeddings
  ↓
512-D Vectors
  ↓
FAISS
```

The generated files are:

```text
vectorstore/image_index.faiss
vectorstore/image_metadata.json
```


---

## 12. FAISS and Metadata Mapping

FAISS stores image vectors while descriptive information is stored separately.

The mapping is positional.

```text
FAISS Vector 0
      ↓
metadata[0]
      ↓
loan_approval_process.png
```

This allows the system to retrieve the original image information after vector search.


---

## 13. Text-to-Image Retrieval

The system supports natural-language image search.

Example:

```text
loan approval process
```

Pipeline:

```text
Text Query
   ↓
CLIP Text Encoder
   ↓
512-D Query Vector
   ↓
FAISS
   ↓
Stored Image Vectors
   ↓
Ranked Images
```

A test produced:

```text
1. loan_approval_process.png      0.3921
2. employee_leave_policy.png      0.2307
3. sales_dashboard.png            0.2251
```

The correct image received the highest score.

This retrieval is based on CLIP vector similarity rather than OCR keyword matching.


---

## 14. Image-to-Image Retrieval

An image can also be used as a search query.

Pipeline:

```text
Query Image
    ↓
CLIP Image Encoder
    ↓
512-D Query Vector
    ↓
FAISS
    ↓
Stored Image Vectors
    ↓
Most Similar Images
```

The main difference is:

```python
# Text-to-image
embedder.embed_text(query)
```

versus:

```python
# Image-to-image
embedder.embed_image(image_path)
```

Both searches use the same FAISS index.


---

## 15. Image-to-Text Context

After retrieving an image, its OCR text and BLIP caption can be converted into textual RAG context.

Example:

```text
Source: employee_leave_policy.png

Caption:
employee pay pay chart

OCR Text:
EMPLOYEE LEAVE POLICY

Annual Leave
24 days per year

Sick Leave
12 days per year
```

The flow becomes:

```text
Relevant Image
     ↓
Metadata
     ↓
OCR + Caption
     ↓
RAG Context
     ↓
LLM
     ↓
Final Answer
```


---

## 16. Retrieval Result vs RAG Context

The retrieval result answers:

```text
Which image is relevant?
```

Example:

```text
employee_leave_policy.png
Similarity Score: 0.42
```

The RAG context answers:

```text
What useful information exists inside that image?
```

Example:

```text
Annual Leave
24 days per year
```

Therefore:

```text
Query
  ↓
Image Retrieval
  ↓
Relevant Image
  ↓
OCR + Caption
  ↓
RAG Context
  ↓
Final Answer
```


---

## 17. Role of Each Component

```text
Tesseract
    ↓
Extract visible text


BLIP
    ↓
Generate image description


CLIP
    ↓
Generate text and image embeddings


FAISS
    ↓
Perform similarity search


Metadata
    ↓
Map vectors to original images


Context Builder
    ↓
Prepare OCR and caption for RAG


LLM
    ↓
Generate final response
```


---

## 18. Complete Architecture

```text
                    IMAGE
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
     Tesseract OCR               BLIP
          │                       │
          ▼                       ▼
     Extracted Text            Caption
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
                   Metadata


                    IMAGE
                      ↓
                     CLIP
                      ↓
               512-D Image Vector
                      ↓
                    FAISS


USER TEXT QUERY
      ↓
CLIP Text Encoder
      ↓
512-D Text Vector
      ↓
FAISS Search
      ↓
Relevant Image
      ↓
Image Metadata
      ↓
OCR + Caption
      ↓
RAG Context
      ↓
LLM / Generator
      ↓
Final Response
```


---

## 19. Current Capabilities

The multimodal module currently supports:

- Image ingestion
- OCR extraction
- Image captioning
- 512-dimensional CLIP embeddings
- FAISS image indexing
- Text-to-image search
- Image-to-image search
- Image-to-text context generation
- Source traceability


---

## 20. Limitations

Current limitations include:

- OCR may produce noisy text for complex images.
- BLIP captions may be generic for text-heavy images.
- The complete FAISS index is rebuilt when new images are added.
- No similarity threshold is currently applied.
- Direct multimodal LLM integration can be added later.


---

## 21. Future Improvements

Possible improvements include:

- OCR text cleaning
- Layout-aware OCR
- Incremental FAISS indexing
- Similarity thresholds
- Metadata filters
- Duplicate image detection
- Better captioning models
- Hybrid OCR + CLIP retrieval
- Multimodal reranking
- GPU acceleration
- Retrieval evaluation


---

## 22. Conclusion

The Multimodal RAG module extends the existing RAG system to support visual enterprise knowledge.

Tesseract extracts visible text from images.

BLIP generates natural-language image descriptions.

CLIP converts both images and text into compatible 512-dimensional vectors.

FAISS stores and searches the image vectors.

Together, the system supports:

```text
Text  → Image
Image → Image
Image → Text
```

Retrieved OCR text, captions and source metadata can then be converted into RAG context and supplied to an LLM for grounded answer generation.