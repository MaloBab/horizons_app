import os
import traceback
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.import_job_service import import_postes_from_file, ALLOWED_EXTENSIONS
from ..schemas.import_job_report import ImportReport

router = APIRouter(prefix="/jobs", tags=["jobs"])

MAX_FILE_SIZE = 10 * 1024 * 1024 


@router.post("/import", response_model=ImportReport, status_code=200)
async def import_jobs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.filename is None:
        raise HTTPException(status_code=422, detail="Nom de fichier manquant")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Format non supporté : {ext}. Formats acceptés : {ALLOWED_EXTENSIONS}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    try:
        tmp_file.write(content)
        tmp_file.close()
        tmp_path: str = tmp_file.name

        report = import_postes_from_file(tmp_path, db)
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")
    finally:
        os.unlink(tmp_file.name)

    return report