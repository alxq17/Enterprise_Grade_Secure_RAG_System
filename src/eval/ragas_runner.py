import math
from typing import Any

from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
)

from src.config.settings import settings
from src.core.logging import app_logger


class RagasRunner:
    """
    Ragas Evaluation Runner for generation quality:
    - Faithfulness: ratio of statements in answer grounded in retrieved context
    - Answer Relevance: degree to which answer addresses original user prompt
    Uses Gemini LLM and Gemini Embeddings.
    """

    def __init__(self):
        self.judge_llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0,
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GEMINI_API_KEY,
        )
        # Crucial: Gemini models only support 1 candidate (n=1) per call
        answer_relevancy.strictness = 1

    def run_evaluation(self, evaluation_records: list[dict[str, Any]]) -> dict[str, float]:
        """
        Accepts records formatted as:
            [
                {
                    "question": str,
                    "contexts": List[str],
                    "answer": str,
                    "ground_truth": str
                }
            ]
        """
        if not evaluation_records:
            return {"faithfulness": 0.0, "answer_relevancy": 0.0}

        app_logger.info(
            f"[RagasRunner] Starting Ragas evaluation on {len(evaluation_records)} records..."
        )

        # Format dataset for Ragas
        data_dict = {
            "question": [str(r["question"]) for r in evaluation_records],
            "contexts": [
                list(r["contexts"]) if isinstance(r["contexts"], list) else [str(r["contexts"])]
                for r in evaluation_records
            ],
            "answer": [str(r["answer"]) for r in evaluation_records],
            "ground_truth": [str(r.get("ground_truth", "")) for r in evaluation_records],
        }
        hf_dataset = Dataset.from_dict(data_dict)

        try:
            result = evaluate(
                dataset=hf_dataset,
                metrics=[faithfulness, answer_relevancy],
                llm=self.judge_llm,
                embeddings=self.embeddings,
            )

            if hasattr(result, "_repr_dict"):
                raw_faithfulness = float(result._repr_dict.get("faithfulness", 0.0))
                raw_relevancy = float(result._repr_dict.get("answer_relevancy", 0.0))
            elif isinstance(result, dict):
                raw_faithfulness = float(result.get("faithfulness", 0.0))
                raw_relevancy = float(result.get("answer_relevancy", 0.0))
            else:
                import numpy as np

                raw_faithfulness = (
                    float(np.nanmean(result["faithfulness"]))
                    if "faithfulness" in getattr(result, "_scores_dict", {})
                    else 0.0
                )
                raw_relevancy = (
                    float(np.nanmean(result["answer_relevancy"]))
                    if "answer_relevancy" in getattr(result, "_scores_dict", {})
                    else 0.0
                )

            f_score = 0.0 if math.isnan(raw_faithfulness) else round(raw_faithfulness, 4)
            r_score = 0.0 if math.isnan(raw_relevancy) else round(raw_relevancy, 4)

        except Exception as e:
            app_logger.error(f"[RagasRunner] Evaluation error: {e}")
            f_score = 0.0
            r_score = 0.0

        scores = {
            "faithfulness": f_score,
            "answer_relevancy": r_score,
        }
        app_logger.info(
            f"[RagasRunner] Completed: Faithfulness={f_score} | AnswerRelevance={r_score}"
        )
        return scores
