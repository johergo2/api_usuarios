from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.usuarios_router import router as usuarios_router
from app.eventos_router import router as eventos_router
from app.participantes_router import router as participantes_router
from app.categorias_router import router as categorias_router
from app.evento_categoria_router import router as evento_categoria_router
from app.participantes_categorias_eventos_router import router as participantes_categorias_eventos_router
from app.jurados_router import router as jurados_router

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
app.include_router(eventos_router, prefix="/api")
app.include_router(participantes_router, prefix="/api")
app.include_router(categorias_router, prefix="/api")
app.include_router(evento_categoria_router, prefix="/api")
app.include_router(participantes_categorias_eventos_router, prefix="/api")
app.include_router(jurados_router, prefix="/api")
