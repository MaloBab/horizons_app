from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
    
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    label: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    pole_id : Mapped[int | None] = mapped_column(Integer, nullable=True)
    preference_id : Mapped[int] = mapped_column(Integer, ForeignKey("preferences.id"), nullable=True)

    preference = relationship("Preference", back_populates="categories")
    jobs       = relationship("Job", back_populates="category")