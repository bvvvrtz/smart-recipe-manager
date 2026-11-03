from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import inventory, recipes

# Automatyczne tworzenie tabel w bazie danych przy starcie
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Fridge AI Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(recipes.router)

@app.get("/")
def serve_home():
    return FileResponse(
        "app/index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )