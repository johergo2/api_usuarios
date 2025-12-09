from fastapi import FastAPI
from app.usuarios_router import router as usuarios_router

app = FastAPI(
    title="API Usuarios",
    description="API para consultar usuarios desde PostgreSQL",
    version="1.0.0"
)

app.include_router(usuarios_router, prefix="/api")
