from pydantic import BaseModel
from typing import Optional, List

class FridgeItemCreate(BaseModel):
    device_id: str
    name: str
    quantity: Optional[str] = "1 szt."
    status: Optional[str] = "active"
    days_left: Optional[int] = 5

class FridgeItemResponse(BaseModel):
    id: int
    device_id: str
    name: str
    quantity: str
    status: str
    days_left: int

    class Config:
        from_attributes = True

class RecipeGenerateRequest(BaseModel):
    device_id: str
    style: Optional[str] = "Dowolny"

class SavedRecipeCreate(BaseModel):
    device_id: str
    title: str
    prep_time: str
    calories: str
    macros: str
    content: str

class SavedRecipeResponse(BaseModel):
    id: int
    device_id: str
    title: str
    prep_time: str
    calories: str
    macros: str
    content: str

    class Config:
        from_attributes = True

class ShoppingItemCreate(BaseModel):
    device_id: str
    name: str

class ShoppingItemResponse(BaseModel):
    id: int
    device_id: str
    name: str
    bought: bool

    class Config:
        from_attributes = True