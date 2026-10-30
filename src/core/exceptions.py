class VeriRAGException(Exception):
    """Base exception for the entire VeriRAG project."""

    pass


class IngestionError(VeriRAGException):
    """An error occurred during the document loading, processing, or chunking phase."""

    pass


class VectorDBError(VeriRAGException):
    """Error connecting to or interacting with Qdrant."""

    pass


class EmbeddingError(VeriRAGException):
    """Error during the BGE-M3 vector generation process."""

    pass
