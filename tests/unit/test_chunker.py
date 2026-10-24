from src.ingestion.chunker import DocumentChunker

def test_chunker_basic():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_docs = [
        {
            "content": "Đây là nội dung thử nghiệm dài dùng để kiểm tra bộ cắt đoạn văn bản. " * 5,
            "metadata": {"source_file": "sample.md", "page_number": 1}
        }
    ]
    chunks = chunker.split_document(sample_docs)

    assert len(chunks) > 1
    assert "chunk_id" in chunks[0]
    assert chunks[0]["metadata"]["source_file"] == "sample.md"
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert chunks[0]["metadata"]["char_count"] <= 100