from fastapi import APIRouter, Depends, HTTPException, Query
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
     usuario_id: int =  Query(..., description="ID del usuario autenticado"),     
     db: AsyncSession = Depends(get_db)
):
    query = text("""
                    SELECT
                        c.id,
                        c.categoria
                    FROM eventos_categorias ec
                    JOIN categorias c 
                       ON c.id = ec.categoria_id
                    JOIN usuarios_eventos ue
                       ON ue.evento_id = ec.evento_id
                    WHERE ec.evento_id = :evento_id
                    AND   ue.usuario_id = :usuario_id
                    ORDER BY c.categoria
    """)

    result = await db.execute(query, {"evento_id": evento_id, "usuario_id": usuario_id})
    categorias = result.mappings().all()

    print("DEBUG → evento_id:", evento_id, "usuario_id:", usuario_id)


    if not categorias:
        raise HTTPException(
            status_code=403,
            detail="El usuario no tiene acceso a este evento o no hay categorías"
        )

    return {
        "evento_id": evento_id,
        "categorias": categorias
    }

# ============================================
# 2. Asignar categorias a un evento
# ============================================
@router.post("/eventos/{evento_id}/categorias")
async def asignar_categorias_evento(evento_id: int, data: dict, db: AsyncSession = Depends(get_db)):
        
        categorias = data.get("categorias", [])

        if not isinstance(categorias, list):
            raise HTTPException(
                status_code=400,
               detail="Debe enviar una lista de categorías"
        )

        # Validar que el evento exista
        evento_query = text("SELECT id FROM eventos WHERE id = :id")
        evento = await db.execute(evento_query, {"id": evento_id})

        if not evento.first():
          raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        try:
            # Eliminar categorías actuales
            #await db.execute(
            #    text("DELETE FROM eventos_categorias WHERE evento_id = :evento_id"),
            #    {"evento_id": evento_id}
            #)

            # Insertar nuevas categorías
            insert_query = text("""
                INSERT INTO eventos_categorias (evento_id, categoria_id)
                VALUES (:evento_id, :categoria_id)
				ON CONFLICT DO NOTHING
            """)

            for categoria_id in categorias:
                await db.execute(
                    insert_query,
                    {
                        "evento_id": evento_id,
                        "categoria_id": categoria_id
                    }
                )

            await db.commit()

            return {
                "message": "Categorías asignadas correctamente",
                "evento_id": evento_id,
                "categorias": categorias
            }

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        


# ============================================
# 3. Eliminar categorias asociadas a evento
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