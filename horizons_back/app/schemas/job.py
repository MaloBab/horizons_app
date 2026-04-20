"""
schemas/job.py
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional
from .category import CategoryCreate, CategoryResponse
from .slot import SlotResponse, SlotCreate

RecruitmentType = Literal["Normal", "Specialise"]


class JobBase(BaseModel):
    name: str = Field(..., min_length=1)
    required_volunteers: int = Field(default=1, ge=1)
    recruitment_type: RecruitmentType = "Normal"
    responsible:         str | None    = None
    sort_order:          int           = 0


class JobCreate(JobBase):
    category: CategoryCreate
    slot:     SlotCreate


class JobUpdate(BaseModel):
    name:                Optional[str]            = Field(None, min_length=1)
    required_volunteers: Optional[int]            = Field(None, ge=1)
    recruitment_type:    Optional[RecruitmentType] = None
    responsible:         Optional[str]            = None
    category_id:         Optional[int]            = None
    slot_id:             Optional[int]            = None


class JobResponse(JobBase):
    id:          int
    category_id: int
    slot_id:     int
    category:    CategoryResponse
    slot:        SlotResponse

    model_config = ConfigDict(from_attributes=True)


class JobGroupResponse(BaseModel):
    """Un poste (nom + type) avec tous ses slots."""
    name:             str
    recruitment_type: RecruitmentType
    responsible:      str | None
    sort_order:       int
    slots:            list[JobResponse]

    model_config = ConfigDict(from_attributes=True)

class CategoryGroupResponse(BaseModel):
    category: CategoryResponse
    jobs:     list[JobGroupResponse]

    model_config = ConfigDict(from_attributes=True)