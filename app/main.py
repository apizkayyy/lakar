from fastapi import FastAPI
from app.routers import health, transcribe, notes, illustrate
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Lakar", description="Speak it. Sketch it.")

for r in (health, transcribe, notes, illustrate):
    app.include_router(r.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")