from pydantic import BaseModel, ConfigDict
from typing import List
from app.schemas.category import CategoryResponse

class PreferenceBase(BaseModel):
    label: str

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int
    categories: List[CategoryResponse] = []
    model_config = ConfigDict(from_attributes=True)
    
class PreferenceUpdate(BaseModel):
    label: str