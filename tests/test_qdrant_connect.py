from qdrant_client import QdrantClient
from src.config.settings import settings

def test_qdrant_connection():
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=5)
    collections = client.get_collections()
    assert collections is not None
    print(f"\n Connect Qdrant Succesfully: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

if __name__ == "__main__":
    test_qdrant_connection()