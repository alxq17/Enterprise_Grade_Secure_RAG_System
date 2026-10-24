import time
from pathlib import Path
from typing import List, Dict, Any
from src.core.logging import app_logger
from src.core.exceptions import IngestionError
from src.ingestion.chunker import DocumentChunker
from src.ingestion.embedder import BGEM3Embedder
from src.ingestion.indexer import QdrantIndexer
from src.ingestion.loaders import DocumentLoader

class IngestionPipeline:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = BGEM3Embedder()
        self.indexer = QdrantIndexer()

    def run_directory(self, raw_dir: str = "data/raw", recreate: bool = False) -> int:
        """read all file in directory raw -> chunk -> embed -> index into Qdrant."""
        path = Path(raw_dir)
        if not path.exists():
            raise IngestionError(f"Directory not exist: {raw_dir}")

        files = [f for f in path.iterdir() if f.suffix.lower() in {".pdf", ".md", ".txt"}]
        if not files:
            app_logger.warning(f"Not find file (.pdf, .md, .txt) in {raw_dir}")
            return 0

        app_logger.info(f"Starting to process  {len(files)} files...")

        # 1 Chunking
        all_chunks: List[Dict[str, Any]] = []
        for file in files:
            try:
                docs = self.loader.load_file(str(file))
                chunks = self.chunker.split_document(docs)
                all_chunks.extend(chunks)
            except Exception as e:
                app_logger.error(f"Error reading file {file.name}: {e}")

        if not all_chunks:
            raise IngestionError("Could not create any chunks from the input data.")

        app_logger.info(f"Created {len(all_chunks)} chunks valid.")

        # 2 Create vector Dense (1024d) + Sparse (lexical weights)
        t0 = time.time()
        texts = [c["text"] for c in all_chunks]
        embeddings = self.embedder.embed_documents(texts, batch_size=8)
        app_logger.info(f"Embedded {len(texts)} chunks in {time.time() - t0:.2f}s")

        # 3. Save into Qdrant
        t1 = time.time()
        self.indexer.create_collection_if_not_exists(recreate=recreate)
        indexed_count = self.indexer.index_chunks(all_chunks, embeddings)
        app_logger.success(
            f"Finished saving {indexed_count} points to the collection '{self.indexer.collection_name}' "
            f"in {time.time() - t1:.2f}s. Total points: {self.indexer.count_points()}"
        )
        return indexed_count