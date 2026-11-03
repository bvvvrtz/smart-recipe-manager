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

class NutritionGoalCreate(BaseModel):
    device_id: str
    calories_goal: int
    protein_goal: int
    fat_goal: int
    carbs_goal: int

class NutritionGoalResponse(BaseModel):
    device_id: str
    calories_goal: int
    protein_goal: int
    fat_goal: int
    carbs_goal: int

    class Config:
        from_attributes = True

class MealLogCreate(BaseModel):
    device_id: str
    date: str
    name: str
    calories: int
    protein: int
    fat: int
    carbs: int

class MealLogResponse(BaseModel):
    id: int
    device_id: str
    date: str
    name: str
    calories: int
    protein: int
    fat: int
    carbs: int

    class Config:
        from_attributes = True