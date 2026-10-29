from pydantic import BaseModel
from typing import Optional, List

# --- Schematy Lodówki ---
class FridgeItemCreate(BaseModel):
    name: str
    quantity: Optional[str] = "1 szt."
    status: Optional[str] = "active"
    days_left: Optional[int] = 5

class FridgeItemResponse(BaseModel):
    id: int
    name: str
    quantity: str
    status: str
    days_left: int

    class Config:
        from_attributes = True

# --- Schematy Generowania i Zapisywania Przepisów ---
class RecipeGenerateRequest(BaseModel):
    style: Optional[str] = "Dowolny"

class SavedRecipeCreate(BaseModel):
    title: str
    prep_time: str
    calories: str
    macros: str
    content: str

class SavedRecipeResponse(BaseModel):
    id: int
    title: str
    prep_time: str
    calories: str
    macros: str
    content: str

    class Config:
        from_attributes = True

# --- Schematy Listy Zakupów ---
class ShoppingItemCreate(BaseModel):
    name: str

class ShoppingItemResponse(BaseModel):
    id: int
    name: str
    bought: bool

    class Config:
        from_attributes = True