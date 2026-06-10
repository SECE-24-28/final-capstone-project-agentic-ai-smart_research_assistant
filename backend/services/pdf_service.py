import fitz
from pathlib import Path
from .config import settings

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class PDFService:
    def __init__(self):
        self.upload_dir = UPLOAD_DIR

    def save_upload(self, file_name: str, content: bytes) -> Path:
        target_path = self.upload_dir / file_name
        target_path.write_bytes(content)
        return target_path

    def extract_text(self, file_path: Path) -> str:
        document = fitz.open(file_path)
        parts = []
        for page in document:
            parts.append(page.get_text())
        return "\n\n".join(parts)

    def chunk_text(self, text: str) -> list[str]:
        max_chars = settings.max_pdf_chunk_chars
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            chunks.append(text[start:end].strip())
            start = end
        return [chunk for chunk in chunks if chunk]

pdf_service = PDFService()
