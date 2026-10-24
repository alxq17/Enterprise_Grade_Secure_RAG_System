from typing import List, Dict, Any
from src.core.logging import app_logger
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, VectorParams, PointStruct, SparseVectorParams, SparseIndexParams, SparseVector)
from src.config.settings import settings

class QdrantIndexer:
     def __init__(self):
          self.client = QdrantClient(
               host=settings.QDRANT_HOST,
               port=settings.QDRANT_PORT,
               api_key=settings.QDRANT_API_KEY or None,
               timeout=60,
          )
          self.collection_name = settings.COLLECTION_NAME
          self.embedding_dim = settings.EMBEDDING_DIM
          app_logger.info(f"[Indexer] Connected to Qdrant {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

     def create_collection_if_not_exists(self, recreate: bool = False):
          """Create collection with dense and sparse. Idempotent"""
          exists = self.client.collection_exists(self.collection_name)
          if exists and recreate:
               app_logger.warning(f"[Indexer] Recreating collection '{self.collection_name}'")
               self.client.delete_collection(self.collection_name)
               exists=False
          if exists:
               app_logger.info(f"[Indexer] Collection '{self.collection_name}' exist.")
               return
          self.client.create_collection(
               collection_name=self.collection_name, 
               vectors_config={"dense": VectorParams(size=self.embedding_dim, distance=Distance.COSINE)},
               sparse_vectors_config={"sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))},
          )
          app_logger.info(f"[Indexer] Created collection '{self.collection_name}' "f"(dense={self.embedding_dim}d + sparse).")

     @staticmethod
     def _to_sparse_vector(lexical_weights: Dict[str, float]) -> SparseVector:
          pairs = []
          for token_str, weight in lexical_weights.items():
               try:
                    token_id = int(token_str)
                    weight = float(weight)
               except (ValueError, TypeError):
                    continue
               if weight > 0:
                    pairs.append((token_id, weight))
          pairs.sort(key=lambda item: item[0])

          return SparseVector( indices=[idx for idx, _ in pairs], values=[val for _, val in pairs],)
     
     def index_chunks(self, chunks: List[Dict[str, Any]], embeddings: Dict[str, list], batch_size: int=64):
          dense_vecs = embeddings["dense_vecs"]
          lexical_weights = embeddings["lexical_weights"]

          assert len(chunks) == len(dense_vecs), (
               "Number of chunks and number of vectors do not match"
          )

          assert len(chunks) == len(lexical_weights), (
               "Nmber of chunks and lexical weights do not match"
          )

          if (batch_size <=0):
               raise ValueError("batch_size must be positive")

          points: List[PointStruct] = []
          for chunk,  dense_vec, lex_w in zip(chunks, dense_vecs, lexical_weights):
               point = PointStruct(
                    id=chunk["chunk_id"],
                    vector={
                         "dense": dense_vec,
                         "sparse": self._to_sparse_vector(lex_w),
                    },
                    payload={
                         "text": chunk["text"],
                         **chunk["metadata"],
                    }
               )
               points.append(point)
          
          # upsert for batch to avoid large payload
          for i in range(0, len(points), batch_size):
               batch = points[i: i+batch_size]
               self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=True,
               )
               app_logger.info(f"[Indexer] Upserted {i + len(batch)} / {len(points)} points")

          return len(points)
          
     def count_points(self) -> int:
          info = self.client.get_collection(self.collection_name)
          return info.points_count
