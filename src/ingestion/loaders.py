from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader, TextLoader

from src.core.logging import app_logger
from src.ingestion.cleaners import TextCleaner


class DocumentLoader:
    def __init__(self):
        self.cleaner = TextCleaner()

    def load_file(self, file_path: str) -> list[dict[str, Any]]:
        """Read the file and return a list of documents with their associated, normalized metadata"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = path.suffix.lower()
        raw_docs = []
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(path))
                raw_docs = loader.load()
            elif ext in [".txt", ".md"]:
                loader = TextLoader(str(path), encoding="utf-8")
                raw_docs = loader.load()
            else:
                app_logger.warning(f"Skip unsupported formats: {ext} ({path.name})")
                return []
        except Exception as e:
            app_logger.error(f"Error reading file {path.name}: {str(e)}")
            raise e
        # data cleaning and packaging
        cleaned_docs = []
        for doc in raw_docs:
            clean_content = self.cleaner.clean(doc.page_content)
            if not clean_content:
                continue
            page_num = doc.metadata.get("page", 0) + 1
            cleaned_docs.append(
                {
                    "content": clean_content,
                    "metadata": {
                        "source_file": path.name,
                        "page_number": page_num,
                        "extension": ext,
                    },
                }
            )

        return cleaned_docs

    def load_directory(self, dir_path: str) -> list[dict[str, Any]]:
        """scan and read all documents in a folder"""
        target_dir = Path(dir_path)
        if not target_dir.is_dir():
            raise NotADirectoryError(f"The path is not a directory: {dir_path}")

        all_docs = []
        for file_path in target_dir.rglob("*"):
            if file_path.suffix.lower() in [".pdf", ".txt", ".md"]:
                docs = self.load_file(str(file_path))
                all_docs.extend(docs)

        app_logger.info(f"Read {len(all_docs)} page/document from a folder: {dir_path}")
        return all_docs
