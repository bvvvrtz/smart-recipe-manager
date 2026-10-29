import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.api import inventory, recipes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Recipe & Fridge Inventory Manager")

app.include_router(inventory.router)
app.include_router(recipes.router)

@app.get("/")
def serve_pwa():
    """Wyświetla mobilną aplikację PWA pod głównym adresem"""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)