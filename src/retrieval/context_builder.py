from typing import Any, Dict, List, Tuple


class ContextBuilder:
  @staticmethod
  def build(chunks: List[Dict[str, Any]],) -> Tuple[str, List[Dict[str, Any]]]:
    """Combine chunks into a context. Return: {context_str, sources}"""
    if not chunks:
     return "", []
    context_parts = []
    sources = []
    seen_sources = set()

    for idx, chunk in enumerate(chunks, 1):
     meta = chunk.get("metadata", {})
     source_file = meta.get("source_file", "unknown")
     page_num = meta.get("page_number", 1)
     text = chunk.get("text", "").strip()

     header = f"[Document {idx} | Source: {source_file} - Page: {page_num}]"
     context_parts.append(f"{header}\n{text}")

     source_key = (source_file, page_num)
     if source_key not in seen_sources:
          seen_sources.add(source_key)
          sources.append({
               "source_file": source_file,
               "page_number": page_num,
               "chunk_id": chunk.get("chunk_id"),
          })
    full_context = "\n\n---\n\n".join(context_parts)
    return full_context, sources