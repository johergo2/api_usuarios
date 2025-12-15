from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

router = APIRouter()

# ============================================
# Obtener sesión de BD (igual a eventos)
# ============================================
async def get_db():
    async with SessionLocal() as session:
        yield session


# ============================================
# 1. Listar categorías de un evento
# GET /api/eventos/{evento_id}/categorias
# ============================================
@router.get("/eventos/{evento_id}/categorias")
async def listar_categorias_evento(
    evento_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            c.id,
            c.categoria
        FROM eventos_categorias ec
        JOIN categorias c ON c.id = ec.categoria_id
        WHERE ec.evento_id = :evento_id
        ORDER BY c.categoria
    """)

    result = await db.execute(query, {"evento_id": evento_id})
    categorias = result.mappings().all()

    return {
        "evento_id": evento_id,
        "categorias": categorias
    }
