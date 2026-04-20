"""
models/job.py — ajout du champ recruitment_type absent du modèle original
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from sqlalchemy.dialects.postgresql import UUID
import enum


class RecruitmentType(str, enum.Enum):
    Normal     = "Normal"
    Specialise = "Specialise"


class Job(Base):
    __tablename__ = "jobs"

    id:                  Mapped[int]            = mapped_column(primary_key=True, autoincrement=True, index=True)
    name:                Mapped[str]
    category_id:         Mapped[int]            = mapped_column(ForeignKey("categories.id"))
    slot_id:             Mapped[int]            = mapped_column(ForeignKey("slots.id"))
    required_volunteers: Mapped[int]            = mapped_column(default=1)
    recruitment_type:    Mapped[RecruitmentType] = mapped_column(default=RecruitmentType.Normal)
    responsible:         Mapped[str | None]     = mapped_column(String, nullable=True)
    sort_order:          Mapped[int]            = mapped_column(default=0)

    category = relationship("Category", back_populates="jobs")
    slot        = relationship("Slot")
    assignments = relationship("Assignment", back_populates="job")


