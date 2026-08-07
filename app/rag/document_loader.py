from pathlib import Path
from fastapi import HTTPException
from pypdf import PdfReader
from docx import Document


def load_document_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8")

        if suffix == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        if suffix == ".docx":
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"文档解析失败：{exc}")

    raise HTTPException(status_code=400, detail="不支持的文件类型")