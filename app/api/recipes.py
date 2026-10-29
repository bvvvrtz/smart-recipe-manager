from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.ai_service import generate_recipe_from_ingredients

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/generate")
def create_recipe(req: schemas.RecipeGenerateRequest = None, db: Session = Depends(get_db)):
    active_items = db.query(models.FridgeItem).filter(models.FridgeItem.status == "active").order_by(models.FridgeItem.days_left.asc()).all()
    
    items_data = [
        {"name": item.name, "quantity": item.quantity, "days_left": item.days_left}
        for item in active_items
    ]
    style = req.style if req else "Dowolny"
    
    recipe_data = generate_recipe_from_ingredients(items_data, style)
    return recipe_data

@router.get("/saved", response_model=List[schemas.SavedRecipeResponse])
def get_saved_recipes(db: Session = Depends(get_db)):
    return db.query(models.SavedRecipe).order_by(models.SavedRecipe.id.desc()).all()

@router.post("/saved", response_model=schemas.SavedRecipeResponse)
def save_recipe(recipe: schemas.SavedRecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.SavedRecipe(**recipe.model_dump())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.delete("/saved/{recipe_id}")
def delete_saved_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(models.SavedRecipe).filter(models.SavedRecipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"message": "Deleted"}