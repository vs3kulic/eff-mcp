"""Index PDF papers into Supabase for EFF RAG.

Usage:
    python scripts/index_papers.py path/to/papers/

Reads credentials from environment (or from .env in project root):
    OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY

Optional flags:
    --chunk-size N       Characters per chunk (default: 1000)
    --overlap N          Character overlap between chunks (default: 200)
    --batch-size N       Embeddings per API call (default: 50)
    --clear              Delete all rows from documents table before indexing

Requires: pip install -e '.[rag,indexing]'
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from supabase import create_client

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200
DEFAULT_BATCH_SIZE = 50
EMBEDDING_MODEL = "text-embedding-3-small"


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        start += size - overlap
    return chunks


def embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [item.embedding for item in response.data]


def index_pdf(
    pdf_path: Path,
    openai_client: OpenAI,
    sb_client,
    chunk_size: int,
    overlap: int,
    batch_size: int,
) -> int:
    print(f"  Extracting text from {pdf_path.name}...")
    text = extract_text(pdf_path)
    if not text.strip():
        print(f"  ! No text extracted from {pdf_path.name}")
        return 0

    chunks = chunk_text(text, chunk_size, overlap)
    print(f"  {len(chunks)} chunks to embed")

    inserted = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = embed_batch(openai_client, batch)
        rows = [
            {"content": content, "source": pdf_path.name, "embedding": embedding}
            for content, embedding in zip(batch, embeddings)
        ]
        sb_client.table("documents").insert(rows).execute()
        inserted += len(batch)
        print(f"  Inserted {inserted}/{len(chunks)}")

    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index PDFs into Supabase for EFF RAG."
    )
    parser.add_argument("path", help="Directory containing PDF files")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all rows from documents table before indexing",
    )
    args = parser.parse_args()

    load_dotenv()

    papers_dir = Path(args.path)
    if not papers_dir.is_dir():
        print(f"Error: {papers_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(papers_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {papers_dir}", file=sys.stderr)
        sys.exit(1)

    for var in ("OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"):
        if not os.getenv(var):
            print(f"Error: {var} environment variable is not set", file=sys.stderr)
            sys.exit(1)

    openai_client = OpenAI()
    sb_client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

    if args.clear:
        print("Clearing documents table...")
        sb_client.table("documents").delete().neq("id", 0).execute()

    print(f"Found {len(pdfs)} PDFs in {papers_dir}")

    total = 0
    failed: list[str] = []
    for pdf in pdfs:
        print(f"\nIndexing: {pdf.name}")
        try:
            total += index_pdf(
                pdf,
                openai_client,
                sb_client,
                args.chunk_size,
                args.overlap,
                args.batch_size,
            )
        except Exception as exc:
            print(f"  ! Failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed.append(pdf.name)

    print(f"\nDone. {total} chunks indexed across {len(pdfs) - len(failed)} PDFs.")
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
