from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.settings import MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
COPY_CHUNK_SIZE = 1024 * 1024


def save_upload_file(file: UploadFile) -> dict:
    filename = Path((file.filename or "").replace("\\", "/")).name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    document_id = uuid4().hex
    save_path = UPLOAD_DIR / f"{document_id}_{filename}"
    bytes_written = 0
    try:
        with save_path.open("wb") as destination:
            while True:
                chunk = file.file.read(COPY_CHUNK_SIZE)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {MAX_UPLOAD_SIZE_BYTES} byte upload limit",
                    )
                destination.write(chunk)
    except HTTPException:
        save_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to save uploaded file") from exc

    if bytes_written == 0:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="File cannot be empty")

    return {
        "document_id": document_id,
        "filename": filename,
        "file_path": str(save_path),
    }
