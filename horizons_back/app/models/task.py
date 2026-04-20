import enum
from typing import Optional
import uuid
import nh3
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, BigInteger, ForeignKey, DateTime, Enum, Table, Uuid
from sqlalchemy.orm import relationship, validates, Mapped, mapped_column

from .base import Base


ALLOWED_TAGS = {
    'p', 'h1', 'h2', 'h3', 'br',
    'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'span',
    'ul', 'ol', 'li',
    'table', 'tbody', 'tr', 'th', 'td'
}

ALLOWED_ATTRIBUTES = {
    'span': {'style'},
    'table': {'style'},
    'th': {'style'},
    'td': {'style'},
    'a': {'href', 'title', 'target'} 
}


class TaskStatus(enum.Enum):
    OPEN      = "open"
    REVIEW    = "review"
    CLOSED    = "closed"

class TaskPriority(enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

class TaskType(enum.Enum):
    STANDARD      = "standard"
    NEEDS_REVIEW  = "needs_review" 

task_tags_table = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",  ForeignKey("tags.id",  ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, unique=True, nullable=False)
    color_hex = Column(String)

    tasks = relationship("Task", secondary=task_tags_table, back_populates="tags")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    type     = Column(Enum(TaskType),     default=TaskType.STANDARD)
    status   = Column(Enum(TaskStatus),   default=TaskStatus.OPEN)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)

    creator_id  = Column(Uuid, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Uuid, ForeignKey("users.id"), nullable=True)

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at               = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    verification_opened_at  = Column(DateTime(timezone=True), nullable=True)
    closed_at               = Column(DateTime(timezone=True), nullable=True)
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tags        = relationship("Tag",             secondary=task_tags_table, back_populates="tasks")
    comments    = relationship("TaskComment",     back_populates="task", cascade="all, delete-orphan")
    subtasks    = relationship("Subtask",         back_populates="task", cascade="all, delete-orphan", order_by="Subtask.position")
    
    assignee    = relationship("User", foreign_keys=[assignee_id])

    @validates("description")
    def sanitize_description(self, key, value):
        if value is None:
            return value
        return nh3.clean(
            value, 
            tags=ALLOWED_TAGS, 
            attributes=ALLOWED_ATTRIBUTES
        )


class TaskComment(Base):
    __tablename__ = "task_comments"

    id        = Column(BigInteger, primary_key=True, index=True)
    task_id   = Column(Uuid, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    content   = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    task   = relationship("Task", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])

    @validates("content")
    def sanitize_content(self, key, value):
        if value is None:
            return value
        return nh3.clean(
            value, 
            tags=ALLOWED_TAGS, 
            attributes=ALLOWED_ATTRIBUTES
        )

class Subtask(Base):
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    task = relationship("Task", back_populates="subtasks")