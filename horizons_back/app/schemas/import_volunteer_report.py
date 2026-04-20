from pydantic import BaseModel
from .volunteer import VolunteerResponse


class ImportWarning(BaseModel):
    ligne: int
    nom: str
    message: str


class ImportError(BaseModel):
    ligne: int
    nom: str | None
    message: str


class ImportReport(BaseModel):
    persisted: list[VolunteerResponse]
    warnings: list[ImportWarning]
    errors: list[ImportError]
    total_parsed: int
    total_persisted: int
    total_warnings: int
    total_errors: int