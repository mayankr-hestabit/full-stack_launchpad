from pathlib import Path
import re

import pandas as pd
import tiktoken
from pypdf import PdfReader
from docx import Document


# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

``
# ---------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------

def clean_text(text):
    """
    Cleans extracted text by:
    - removing excessive whitespace
    - removing unnecessary newlines/tabs
    - trimming leading/trailing spaces
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# TOKEN-BASED CHUNKING
# ---------------------------------------------------------

def chunk_text(text, chunk_size=600, overlap=100):
    """
    Splits text into token-based chunks.

    Default:
    chunk_size = 600 tokens
    overlap = 100 tokens
    """

    if not text:
        return []

    encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)

    chunks = []

    start = 0

    while start < len(tokens):

        end = start + chunk_size

        chunk_tokens = tokens[start:end]

        chunk = encoding.decode(chunk_tokens)

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------
# METADATA ASSIGNMENT
# ---------------------------------------------------------

def assign_metadata(
    chunks,
    source,
    file_type,
    page_number=None,
    tags=None
):
    """
    Adds metadata to every chunk.
    """

    if tags is None:
        tags = []

    records = []

    for index, chunk in enumerate(chunks, start=1):

        records.append({
            "chunk_id": index,
            "text": chunk,
            "source": source,
            "file_type": file_type,
            "page_number": page_number,
            "tags": tags
        })

    return records


# ---------------------------------------------------------
# TXT LOADER
# ---------------------------------------------------------

def load_txt(file_path):
    """
    Loads plain text files.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ---------------------------------------------------------
# DOCX LOADER
# ---------------------------------------------------------

def load_docx(file_path):
    """
    Loads text from DOCX paragraphs.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# ---------------------------------------------------------
# CSV LOADER
# ---------------------------------------------------------

def load_csv(file_path):
    """
    Loads CSV and converts tabular data into text.
    """

    dataframe = pd.read_csv(file_path)

    return dataframe.to_string(index=False)


# ---------------------------------------------------------
# PDF LOADER
# ---------------------------------------------------------

def load_pdf(file_path):
    """
    Loads PDF page-by-page.

    Page numbers are preserved so that
    chunks can later be traced back to their source page.
    """

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    return pages


# ---------------------------------------------------------
# MAIN DOCUMENT PROCESSOR
# ---------------------------------------------------------

def load_document(file_path):
    """
    Detects file type and processes it through:

    load
        ↓
    clean
        ↓
    chunk
        ↓
    metadata

    Supported formats:
    TXT
    PDF
    DOCX
    CSV
    """

    file_path = Path(file_path)

    extension = file_path.suffix.lower()


    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------

    if extension == ".txt":

        text = load_txt(file_path)

        cleaned_text = clean_text(text)

        chunks = chunk_text(cleaned_text)

        return assign_metadata(
            chunks=chunks,
            source=file_path.name,
            file_type=extension,
            page_number=None,
            tags=["text"]
        )


    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    elif extension == ".docx":

        text = load_docx(file_path)

        cleaned_text = clean_text(text)

        chunks = chunk_text(cleaned_text)

        return assign_metadata(
            chunks=chunks,
            source=file_path.name,
            file_type=extension,
            page_number=None,
            tags=["document"]
        )


    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    elif extension == ".csv":

        text = load_csv(file_path)

        cleaned_text = clean_text(text)

        chunks = chunk_text(cleaned_text)

        return assign_metadata(
            chunks=chunks,
            source=file_path.name,
            file_type=extension,
            page_number=None,
            tags=["csv"]
        )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    elif extension == ".pdf":

        pages = load_pdf(file_path)

        all_chunks = []

        for page in pages:

            cleaned_text = clean_text(
                page["text"]
            )

            if not cleaned_text:
                continue

            chunks = chunk_text(
                cleaned_text
            )

            page_chunks = assign_metadata(
                chunks=chunks,
                source=file_path.name,
                file_type=extension,
                page_number=page["page_number"],
                tags=["pdf"]
            )

            all_chunks.extend(page_chunks)

        return all_chunks


    # -----------------------------------------------------
    # UNSUPPORTED FILE
    # -----------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


# ---------------------------------------------------------
# INGEST ALL DOCUMENTS FROM data/raw
# ---------------------------------------------------------

def ingest_raw_documents():
    """
    Processes every supported document inside data/raw.
    """

    documents = []

    for file_path in RAW_DATA_DIR.iterdir():

        if not file_path.is_file():
            continue

        try:

            chunks = load_document(file_path)

            documents.append({
                "source": file_path.name,
                "file_type": file_path.suffix.lower(),
                "chunks": chunks
            })

            print(
                f"Loaded: {file_path.name} "
                f"({len(chunks)} chunks)"
            )

        except Exception as error:

            print(
                f"Failed to load {file_path.name}: "
                f"{error}"
            )

    return documents


# ---------------------------------------------------------
# TEST PIPELINE
# ---------------------------------------------------------

if __name__ == "__main__":

    documents = ingest_raw_documents()

    print(
        f"\nTotal documents loaded: "
        f"{len(documents)}"
    )

    for document in documents:

        print(
            "\n===================================="
        )

        print(
            f"Document: {document['source']}"
        )

        print(
            f"Type: {document['file_type']}"
        )

        print(
            f"Chunks: {len(document['chunks'])}"
        )

        for chunk in document["chunks"]:

            print("\n--- Chunk ---")

            print(
                "Chunk ID:",
                chunk["chunk_id"]
            )

            print(
                "Source:",
                chunk["source"]
            )

            print(
                "File Type:",
                chunk["file_type"]
            )

            print(
                "Page Number:",
                chunk["page_number"]
            )

            print(
                "Tags:",
                chunk["tags"]
            )

            print(
                "Text:",
                chunk["text"][:300]
            )