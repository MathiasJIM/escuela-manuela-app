from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.api.v1.api_router import api_router

app = FastAPI(title="Sistema Escolar - Escuela Manuela Santamaría")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["now"] = datetime.utcnow


@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Inicio • Escuela Manuela Santamaría"},
    )

# Placeholder: Junta y Patronato
@app.get("/junta-patronato", response_class=HTMLResponse, name="junta_patronato")
async def junta_patronato(request: Request):
    return templates.TemplateResponse(
        "junta_patronato.html",
        {"request": request, "page_title": "Junta y Patronato"}
    )

# Placeholder: Login
@app.get("/login", response_class=HTMLResponse, name="login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "page_title": "Acceder al Portal"}
    )

# Salud JSON para monitoreo
@app.get("/api/health", tags=["Base"])
def health():
    return JSONResponse({"status": "ok", "service": "escuela-api"})

# Rutas de API existentes
app.include_router(api_router)
