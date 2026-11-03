from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base

class FridgeItem(Base):
    __tablename__ = "fridge_items"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    quantity = Column(String, default="1 szt.")
    status = Column(String, default="active")
    days_left = Column(Integer, default=5)

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    prep_time = Column(String)
    calories = Column(String)
    macros = Column(String)
    content = Column(Text, nullable=False)

class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    bought = Column(Boolean, default=False)

class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    calories_goal = Column(Integer, default=2400)
    protein_goal = Column(Integer, default=160)
    fat_goal = Column(Integer, default=75)
    carbs_goal = Column(Integer, default=270)

class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)  # Format YYYY-MM-DD
    name = Column(String, nullable=False)
    calories = Column(Integer, default=0)
    protein = Column(Integer, default=0)
    fat = Column(Integer, default=0)
    carbs = Column(Integer, default=0)