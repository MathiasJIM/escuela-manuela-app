from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router

app = FastAPI(title="Sistema Escolar - Escuela Manuela Santamaría")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(api_router)

@app.get("/", tags=["Base"])
def read_root():
    return {"mensaje": "Sistema activo 🚀"}