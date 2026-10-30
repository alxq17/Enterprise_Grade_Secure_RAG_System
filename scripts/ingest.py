"""
Entrypoint: readc data/raw/ → chunk → embed → index vào Qdrant.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingestion.pipeline import IngestionPipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest data into Qdrant")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete the existing collection and recreate it (Attention: this will result in the loss of existing data)",
    )
    args = parser.parse_args()
    pipeline = IngestionPipeline()
    pipeline.run_directory("data/raw", recreate=args.recreate)
