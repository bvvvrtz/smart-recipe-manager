import base64
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.ai_service import analyze_image_for_ingredients

router = APIRouter(prefix="/inventory", tags=["Inventory & Shopping"])

# --- LODÓWKA ---
@router.get("/", response_model=List[schemas.FridgeItemResponse])
def get_inventory(db: Session = Depends(get_db)):
    # Sortujemy tak, aby produkty z najkrótszą datą ważności były na samej górze!
    return db.query(models.FridgeItem).order_by(models.FridgeItem.days_left.asc()).all()

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

@router.delete("/")
def clear_inventory(db: Session = Depends(get_db)):
    db.query(models.FridgeItem).delete()
    db.commit()
    return {"message": "Wszystkie produkty zostały usunięte"}

@router.post("/scan")
async def scan_inventory_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")
    
    detected_items = analyze_image_for_ingredients(image_base64)
    
    added_names = []
    for item in detected_items:
        name = item.get("name", "Produkt")
        qty = item.get("quantity", "1 szt.")
        days = item.get("days_left", 5)
        new_item = models.FridgeItem(name=name, quantity=qty, status="active", days_left=days)
        db.add(new_item)
        added_names.append(name)
    
    db.commit()
    return {
        "message": f"Dodano {len(added_names)} produktów!",
        "detected_items": added_names
    }

# --- LISTA ZAKUPÓW ---
@router.get("/shopping", response_model=List[schemas.ShoppingItemResponse])
def get_shopping_list(db: Session = Depends(get_db)):
    return db.query(models.ShoppingItem).all()

@router.post("/shopping", response_model=schemas.ShoppingItemResponse)
def add_shopping_item(item: schemas.ShoppingItemCreate, db: Session = Depends(get_db)):
    db_item = models.ShoppingItem(name=item.name, bought=False)
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

@router.delete("/shopping/clear")
def clear_shopping_list(db: Session = Depends(get_db)):
    db.query(models.ShoppingItem).delete()
    db.commit()
    return {"message": "Lista zakupów wyczyszczona"}