from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.usuarios_router import router as usuarios_router

app = FastAPI(
    title="API Usuarios",
    description="API para consultar usuarios desde PostgreSQL",
    version="1.0.0"
)

# ==== HABILITAR CORS ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Permitir cualquier origen (para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== RUTAS ====
app.include_router(usuarios_router, prefix="/api")
