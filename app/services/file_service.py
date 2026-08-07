from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


def save_upload_file(file: UploadFile) -> dict:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件不能为空")

    document_id = uuid4().hex
    save_path = UPLOAD_DIR / f"{document_id}_{filename}"
    save_path.write_bytes(content)

    return {
        "document_id": document_id,
        "filename": filename,
        "file_path": str(save_path),
    }