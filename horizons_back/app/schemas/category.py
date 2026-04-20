from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    label: str
    preference_id: int

class CategoryCreate(BaseModel):
    """Création de catégorie — import ou manuelle."""
    label:         str
    pole_id:       int | None = None
    preference_id: int | None = None


class CategoryUpdate(BaseModel):
    label:         str | None = None
    pole_id:       int | None = None
    preference_id: int | None = None


class CategoryResponse(BaseModel):
    id:            int
    label:         str
    pole_id:       int | None = None
    preference_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
