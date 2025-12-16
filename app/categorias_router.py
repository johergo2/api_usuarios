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
# 1. Listar categorías
# GET /api/categorias
# ============================================
@router.get("/categorias")
async def listar_categorias(db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            id,
            categoria
        FROM categorias
        ORDER BY categoria
    """)

    result = await db.execute(query)
    rows = result.mappings().all()

    return {"categorias": rows}



# ============================================
# 2. Listar categorías de un evento
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
# 3. Crear categoria
# ============================================
@router.post("/categorias")
async def crear_categoria(categoria: dict, db: AsyncSession = Depends(get_db)):

    print("📌 Datos recibidos en crear_categoria:", categoria)
    
    query = text("""
        INSERT INTO categorias (categoria)
        VALUES (:categoria)
        RETURNING *;
    """)

    result = await db.execute(query, categoria)
    nueva_categoria = result.mappings().first()
    await db.commit()

    return nueva_categoria

# ============================================
# 4. Actualizar categoria
# ============================================
@router.put("/categoria/{id}")
async def actualizar_categoria(id: int, datos: dict, db: AsyncSession = Depends(get_db)):

    datos["id"] = id

    query = text("""
        UPDATE categorias
        SET categoria = :categoria,                        
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

  
    result = await db.execute(query, datos)
    categoria = result.mappings().first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    await db.commit()
    return categoria


# ============================================
# 5. Eliminar categoria
# ============================================
@router.delete("/categoria/{id}")
async def eliminar_categoria(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM categorias WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    categoria = result.mappings().first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    await db.commit()
    return {"message": "categoria eliminada correctamente", "id": id}
