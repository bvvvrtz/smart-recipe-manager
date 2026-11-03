import base64
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.ai_service import analyze_image_for_ingredients, estimate_meal_macros

router = APIRouter(prefix="/inventory", tags=["Inventory, Shopping & Nutrition"])

# --- LODÓWKA ---
@router.get("/", response_model=List[schemas.FridgeItemResponse])
def get_inventory(device_id: str, db: Session = Depends(get_db)):
    return db.query(models.FridgeItem).filter(models.FridgeItem.device_id == device_id).order_by(models.FridgeItem.days_left.asc()).all()

@router.post("/", response_model=schemas.FridgeItemResponse)
def add_item(item: schemas.FridgeItemCreate, db: Session = Depends(get_db)):
    db_item = models.FridgeItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.FridgeItem).filter(models.FridgeItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

@router.delete("/clear/{device_id}")
def clear_inventory(device_id: str, db: Session = Depends(get_db)):
    db.query(models.FridgeItem).filter(models.FridgeItem.device_id == device_id).delete()
    db.commit()
    return {"message": "Wszystkie produkty użytkownika zostały usunięte"}

@router.post("/scan")
async def scan_inventory_image(device_id: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")
    
    detected_items = analyze_image_for_ingredients(image_base64)
    
    added_names = []
    for item in detected_items:
        name = item.get("name", "Produkt")
        qty = item.get("quantity", "1 szt.")
        days = item.get("days_left", 5)
        new_item = models.FridgeItem(device_id=device_id, name=name, quantity=qty, status="active", days_left=days)
        db.add(new_item)
        added_names.append(name)
    
    db.commit()
    return {
        "message": f"Dodano {len(added_names)} produktów!",
        "detected_items": added_names
    }

# --- LISTA ZAKUPÓW ---
@router.get("/shopping", response_model=List[schemas.ShoppingItemResponse])
def get_shopping_list(device_id: str, db: Session = Depends(get_db)):
    return db.query(models.ShoppingItem).filter(models.ShoppingItem.device_id == device_id).all()

@router.post("/shopping", response_model=schemas.ShoppingItemResponse)
def add_shopping_item(item: schemas.ShoppingItemCreate, db: Session = Depends(get_db)):
    db_item = models.ShoppingItem(device_id=item.device_id, name=item.name, bought=False)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/shopping/{item_id}")
def toggle_shopping_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.ShoppingItem).filter(models.ShoppingItem.id == item_id).first()
    if db_item:
        db_item.bought = not db_item.bought
        db.commit()
    return {"message": "Updated"}

@router.delete("/shopping/clear/{device_id}")
def clear_shopping_list(device_id: str, db: Session = Depends(get_db)):
    db.query(models.ShoppingItem).filter(models.ShoppingItem.device_id == device_id).delete()
    db.commit()
    return {"message": "Lista zakupów wyczyszczona"}

# --- FITATU: CELE I KALORIE ---
@router.get("/nutrition/goal", response_model=schemas.NutritionGoalResponse)
def get_nutrition_goal(device_id: str, db: Session = Depends(get_db)):
    goal = db.query(models.NutritionGoal).filter(models.NutritionGoal.device_id == device_id).first()
    if not goal:
        goal = models.NutritionGoal(
            device_id=device_id,
            calories_goal=2400,
            protein_goal=160,
            fat_goal=75,
            carbs_goal=270
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal

@router.post("/nutrition/goal", response_model=schemas.NutritionGoalResponse)
def set_nutrition_goal(data: schemas.NutritionGoalCreate, db: Session = Depends(get_db)):
    goal = db.query(models.NutritionGoal).filter(models.NutritionGoal.device_id == data.device_id).first()
    if not goal:
        goal = models.NutritionGoal(**data.model_dump())
        db.add(goal)
    else:
        goal.calories_goal = data.calories_goal
        goal.protein_goal = data.protein_goal
        goal.fat_goal = data.fat_goal
        goal.carbs_goal = data.carbs_goal
    db.commit()
    db.refresh(goal)
    return goal

@router.get("/nutrition/logs", response_model=List[schemas.MealLogResponse])
def get_meal_logs(device_id: str, date: str, db: Session = Depends(get_db)):
    return db.query(models.MealLog).filter(
        models.MealLog.device_id == device_id,
        models.MealLog.date == date
    ).order_by(models.MealLog.id.desc()).all()

@router.post("/nutrition/logs", response_model=schemas.MealLogResponse)
def add_meal_log(log: schemas.MealLogCreate, db: Session = Depends(get_db)):
    db_log = models.MealLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.post("/nutrition/estimate-and-log", response_model=schemas.MealLogResponse)
def estimate_and_log_meal(data: schemas.MealEstimateRequest, db: Session = Depends(get_db)):
    estimated = estimate_meal_macros(data.description)
    db_log = models.MealLog(
        device_id=data.device_id,
        date=data.date,
        name=estimated.get("name", data.description),
        calories=estimated.get("calories", 0),
        protein=estimated.get("protein", 0),
        fat=estimated.get("fat", 0),
        carbs=estimated.get("carbs", 0)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.delete("/nutrition/logs/{log_id}")
def delete_meal_log(log_id: int, db: Session = Depends(get_db)):
    db_log = db.query(models.MealLog).filter(models.MealLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"message": "Deleted"}