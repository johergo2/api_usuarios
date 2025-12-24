from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()

class CalificacionCreate(BaseModel):
    cedula_jurado: str = Field(..., max_length=20)
    cedula_participan: str = Field(..., max_length=20)
    evento_id: int
    categoria_id: int
    puntaje: Decimal = Field(..., ge=0, le=100)

# ============================================
# Obtener sesión de BD (igual a eventos)
# ============================================
async def get_db():
    async with SessionLocal() as session:
        yield session

# ============================================
# 1. Listar calificaciones
# GET /api/calificaciones
# ============================================
@router.get("/calificaciones")
async def listar_calificaciones(db: AsyncSession = Depends(get_db)
):
    query = text("""
                  SELECT 
                      id,
                      cedula_jurado,
                      cedula_participan,
                      evento_id,
                      categoria_id,
                      puntaje
                  FROM calificaciones
                  ORDER BY id
                """)

    result = await db.execute(query)
    rows = result.mappings().all()

    return {"calificaciones": rows}

# ============================================
# 1A. Listar calificaciones Total
# GET /api/calificacionestot
# ============================================
@router.get("/calificacionestot")
async def listar_calificacionestot(db: AsyncSession = Depends(get_db)
):
    query = text("""
                    SELECT
                    c.id,
                    j.cedula||'-'||j.nombre        AS jurado,
                    e.id||'-'||e.nombre        AS evento,
                    cat.id||'-'||cat.categoria   AS categoria,
                    p.id||'-'||p.nombre        AS participante,
                    c.puntaje
                    FROM calificaciones c, jurados j, eventos e, categorias cat, participantes p
                    WHERE j.cedula = c.cedula_jurado
                    AND   e.id = c.evento_id
                    AND   cat.id = c.categoria_id
                    AND   p.cedula = c.cedula_participan
                  ORDER BY e.id
                """)

    result = await db.execute(query)
    rows = result.mappings().all()

    return {"calificacionestot": rows}


# ============================================
# 2. Listar calificaciones de un evento
# GET /api/eventos/{evento_id}/calificaciones
# ============================================
@router.get("/eventos/{evento_id}/calificaciones")
async def listar_calificaciones_evento(
    evento_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
                  SELECT 
                      id,
                      cedula_jurado,
                      cedula_participan,
                      evento_id,
                      categoria_id,
                      puntaje
                  FROM calificaciones
                  WHERE evento_id = :evento_id
                  ORDER BY evento_id
                """)

    result = await db.execute(query, {"evento_id": evento_id})
    calificaciones = result.mappings().all()

    return {
        "evento_id": evento_id,
        "calificaciones": calificaciones
    }

# ============================================
# 3. Crear calificacion
# ============================================
@router.post("/calificaciones")
async def crear_calificacion(
    data: CalificacionCreate, 
    db: AsyncSession = Depends(get_db)
):


    print("📌 Datos recibidos en crear_calificacion:", data.dict())
    
    query = text("""
        INSERT INTO calificaciones (cedula_jurado, cedula_participan, evento_id, categoria_id, puntaje)
        VALUES (:cedula_jurado, :cedula_participan, :evento_id, :categoria_id, :puntaje )
        RETURNING *;
    """)

    result = await db.execute(query, data.dict())
    nueva_calificacion = result.mappings().first()
    await db.commit()

    return nueva_calificacion

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
