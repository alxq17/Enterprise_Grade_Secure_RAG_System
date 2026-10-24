import time
from typing import Dict, Any
from google import genai
from google.genai import types
from src.core.logging import app_logger
from src.config.settings import settings
from src.core.exceptions import VeriRAGException

class LLMError(VeriRAGException):
     pass

class GeminiClient:
     def __init__(self):
          if not settings.GEMINI_API_KEY:
               app_logger.info(f"[GeminiClient] GEMINI_API_KEY has not been configured in .env!")
          self.client = genai.Client(api_key = settings.GEMINI_API_KEY)
          self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
          app_logger.info("[GeminiClient] Ready with model: {self.model_name}")
     def generate_answer(self, query: str, context: str) -> Dict[str, Any]:
          if not context.strip():
               return {
                    "answer": "I cannot find relevant information in the internal documentation to answer this question.",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "latency_ms": 0.0
               }
          system_instruction = (
               "You are a professional AI assistant designed to query a company's internal documents (VeriRAG).\n"
            "MANDATORY PRINCIPLES:\n"
            "1. Base your answers solely on the information provided in the 'DOCUMENT CONTEXT' section.\n"
            "2. Do not speculate or add any information outside of the provided documents.\n"
            "3. If the context does not contain the information needed to answer, state exactly: "
            "'The provided documents do not contain information regarding this question.'\n"
            "4. At the end of each point, cite the source clearly using the format: [File_name - Page X]."
          )

          prompt = f"""DOCUMENT CONTEXT: {context} --- USER QUESTION: {query} ANSWER:"""
          t0 = time.time()
          try: 
               reponse = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1,)
               )
               latency_ms = round((time.time() - t0) * 1000, 2)
               usage = getattr(reponse, "usage_metadata", None)
               input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
               output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
          except Exception as e:
               app_logger.error(f"[GeminiClient] Error calling Gemini {e}")
               raise LLMError(f"Error connecting to the Gemini model: {e}")