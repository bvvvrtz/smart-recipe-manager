from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base

class FridgeItem(Base):
    __tablename__ = "fridge_items"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)  # Unikalne ID telefonu
    name = Column(String, index=True, nullable=False)
    quantity = Column(String, default="1 szt.")
    status = Column(String, default="active")
    days_left = Column(Integer, default=5)

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)  # Unikalne ID telefonu
    title = Column(String, nullable=False)
    prep_time = Column(String)
    calories = Column(String)
    macros = Column(String)
    content = Column(Text, nullable=False)

class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)  # Unikalne ID telefonu
    name = Column(String, nullable=False)
    bought = Column(Boolean, default=False)