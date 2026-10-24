import uuid 
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.logging import app_logger

class DocumentChunker:
     def __init__ (self, chunk_size: int = 512, chunk_overlap: int = 50):
          self.chunk_size = chunk_size
          self.chunk_overlap = chunk_overlap
          self.splitter = RecursiveCharacterTextSplitter(
               chunk_size = self.chunk_size,
               chunk_overlap = self.chunk_overlap,
               length_function = len,
               separators = ["\n\n", "\n", ". ", " ", ""],
          )
     def split_document(self, document: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
          chunks = []
          for doc in document:
               text = doc["content"]
               base_meta = doc["metadata"]
               split_texts = self.splitter.split_text(text)

               for idx, split_text in enumerate(split_texts):
                chunk_id = str(uuid.uuid4())
                chunk_meta = {
                    **base_meta,
                    "chunk_id": chunk_id,
                    "chunk_index": idx,
                    "char_count": len(split_text)
                }
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": split_text,
                    "metadata": chunk_meta
                })

          if chunks:
               avg_len = sum(c["metadata"]["char_count"] for c in chunks) // len(chunks)
               app_logger.info(
                    f"Created {len(chunks)} chunks | Average length: {avg_len} words "
                    f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
               )
          else:
               app_logger.warning("No chunks were generated from the input text.")

          return chunks