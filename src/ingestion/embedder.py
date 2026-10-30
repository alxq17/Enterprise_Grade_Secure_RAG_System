from FlagEmbedding import BGEM3FlagModel

from src.config.settings import settings
from src.core.logging import app_logger


class BGEM3Embedder:
    """Wrapper for BGE-M3, return dense vector and sparse"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str | None = None, use_fp16: bool = False):
        if self._initialized:
            return
        self.model_name = model_name or settings.EMBEDDING_MODEL
        app_logger.info(f"[Embedder] Loading {self.model_name}...")
        self.model = BGEM3FlagModel(self.model_name, use_fp16=use_fp16)
        self._initialized = True
        app_logger.info("[Embedder] Model ready.")

    def embed_documents(self, texts: list[str], batch_size: int = 8) -> dict[str, list]:
        """Return dict:
        - 'dense_vecs': List[List[float]] — shape (N, 1024)
        - 'lexical_weights': List[Dict[str, float]] — sparse weights
        """
        if not texts:
            return {"dense_vecs": [], "lexical_weights": []}

        app_logger.info(f"[Embedder] Encoding {len(texts)} texts (batch={batch_size})...")
        output = self.model.encode(
            texts,
            batch_size=batch_size,
            max_length=512,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        return {
            "dense_vecs": output["dense_vecs"].tolist(),
            "lexical_weights": output["lexical_weights"],
        }

    def embed_query(self, query: str) -> dict[str, list]:
        return self.embed_documents([query], batch_size=1)
