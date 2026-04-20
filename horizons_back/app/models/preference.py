from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Preference(Base):
    __tablename__ = "preferences"

    id    = Column(Integer, primary_key=True, autoincrement=True, index=True)
    label = Column(String, nullable=False, unique=True)

    categories = relationship("Category", back_populates="preference", cascade="all, delete-orphan")