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

# ============================================
# 2. Crear categorias_evento
# ============================================
@router.post("/eventos/{evento_id}/categorias")
async def crear_categorias_evento(cat_evento: dict, db: AsyncSession = Depends(get_db)):
        
        query = text("""
        INSERT INTO eventos_categorias (evento_id, categoria_id)
        VALUES (:evento_id, :categoria_id)
        RETURNING *;
    """)
        
        result = await db.execute(query, cat_evento)
        nuevo_evento = result.mappings().first()
        await db.commit()

        return nuevo_evento


# ============================================
# 3. Actualizar evento
# ============================================
@router.put("/eventos/{evento_id}/categorias")
async def actualizar_categorias_evento(evento_id: int, datos: dict, db: AsyncSession = Depends(get_db)):
     
    datos["evento_id"] = evento_id

    query = text("""
        UPDATE eventos_categorias
        SET categoria_id = :categoria_id
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :evento_id
        RETURNING *;
    """)

    result = await db.execute(query, datos)
    evento = result.mappings().first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    await db.commit()
    return evento   

# ============================================
# 4. Eliminar evento
# ============================================ 
@router.delete("/eventos/{evento_id}/categorias/{categoria_id}")
async def eliminar_categorias_evento(evento_id: int, categoria_id: int, db: AsyncSession = Depends(get_db)):
     
     query = text("""DELETE FROM eventos_categorias
                  WHERE evento_id = :evento_id
                  AND categoria_id = :categoria_id
                  RETURNING id""")

     result = await db.execute(query, {"evento_id": evento_id,
                                      "categoria_id": categoria_id})
     eliminado = result.first()

     if not eliminado:
            raise HTTPException(
                status_code=404,
                detail="La categoría no está asignada a este evento"
        )     
     await db.commit()

     return {
        "message": "Categoría eliminada del evento",
        "evento_id": evento_id,
        "categoria_id": categoria_id
     }