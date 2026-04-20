from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from uuid import UUID

class Assignment(Base):
    __tablename__ = "assignments"

    # Notice how we specify the Python types (UUID, int) inside Mapped[]
    volunteer_id: Mapped[UUID] = mapped_column(ForeignKey("volunteers.id"), primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), primary_key=True)

    volunteer = relationship("Volunteer", back_populates="assignments")
    job = relationship("Job", back_populates="assignments")