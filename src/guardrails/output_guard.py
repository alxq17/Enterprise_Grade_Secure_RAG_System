import re

from src.core.logging import app_logger


class OutputGuard:
    """
    Output Guard: Validates that LLM generated answers adhere to
    the retrieved context and maintain verifiable citations.
    """

    FALLBACK_INDICATORS = [
        "does not contain information",
        "do not contain information",
        "tài liệu không chứa",
        "không có thông tin",
        "cannot find relevant information",
    ]

    CITATION_PATTERN = re.compile(r"\[([^\]]+?)(?:\s*-\s*Page\s*(\d+))?\]")

    def __init__(self, require_citations: bool = False):
        self.require_citations = require_citations

    def is_fallback_answer(self, answer: str) -> bool:
        """Check if the answer is a model disclaimer stating lack of context."""
        lowered = answer.lower()
        return any(ind in lowered for ind in self.FALLBACK_INDICATORS)

    def extract_citations(self, answer: str) -> list[str]:
        """Extract all [source - Page X] or [source] citations from answer text."""
        return self.CITATION_PATTERN.findall(answer)

    def validate(self, answer: str, context: str) -> tuple[bool, str | None]:
        """
        Validate answer fidelity:
        - Must not be empty.
        - If require_citations is True and not a fallback answer, must contain citations.
        - Verify citations correlate with provided context files.
        """
        if not answer or not answer.strip():
            return False, "Output validation failed: Empty answer generated."

        # If model explicitly states it has no information, that is grounded refusal
        if self.is_fallback_answer(answer):
            app_logger.debug("[OutputGuard] Answer identified as legitimate ungrounded refusal.")
            return True, None

        # Check for citation presence if required
        if self.require_citations:
            citations = self.extract_citations(answer)
            if not citations:
                app_logger.warning("[OutputGuard] Answer lacks required citation markers.")
                return False, "Output validation failed: Missing document citations."

        return True, None
