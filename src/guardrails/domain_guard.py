from typing import Any

from src.config.settings import settings
from src.core.logging import app_logger


class DomainGuard:
    """
    Domain similarity gate: checks whether retrieved chunks meet minimum
    similarity threshold (default: 0.35). If top-1 chunk score is below threshold,
    the query is marked out-of-domain and the pipeline short-circuits.
    """

    def __init__(self, threshold: float | None = None):
        self.threshold = (
            threshold if threshold is not None else settings.DOMAIN_SIMILARITY_THRESHOLD
        )

    def is_in_domain(self, top_chunks: list[dict[str, Any]]) -> bool:
        """Check if top retrieval results meet minimum relevance threshold."""
        if not top_chunks or len(top_chunks) == 0:
            app_logger.warning("[DomainGuard] No chunks returned from Retrieval layer.")
            return False

        # Get rerank_score from top chunk
        top_score = float(top_chunks[0].get("rerank_score", 0.0))
        if top_score < self.threshold:
            app_logger.warning(
                f"[DomainGuard] Query outside domain scope: Top Score ({top_score:.4f}) < Threshold ({self.threshold})"
            )
            return False

        app_logger.debug(
            f"[DomainGuard] Query in domain: Top Score ({top_score:.4f}) >= Threshold ({self.threshold})"
        )
        return True
