from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

router = APIRouter()

class CalificacionCreate(BaseModel):
    cedula_jurado: str = Field(..., max_length=20)
    cedula_participan: str = Field(..., max_length=20)
    evento_id: int
    categoria_id: int
    puntaje: Decimal = Field(..., ge=0, le=100)

class CalificacionPromedioCreate(BaseModel):
    cedula_jurado: str
    cedula_participan: str    
    evento_id: int
    categoria_id: int
    promedio: float    

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
# 1A. Listar calificaciones Total (con descripciones)
# GET /api/calificacionestot
# ============================================
@router.get("/calificacionestot")
async def listar_calificacionestot(evento_id: Optional[int] = Query(None), 
                                   db: AsyncSession = Depends(get_db)
):
    query = """
                    SELECT
                    c.id,
                    j.cedula        AS cedula_jurado,
                    j.nombre        AS jurado,
                    e.id            AS evento_id,
                    e.nombre        AS evento,
                    cat.id          AS categoria_id,
                    cat.categoria   AS categoria,
                    p.cedula        AS cedula_participan,
                    p.nombre        AS participante,
                    c.puntaje
                    FROM calificaciones c, jurados j, eventos e, categorias cat, participantes p
                    WHERE j.cedula = c.cedula_jurado
                    AND   e.id = c.evento_id
                    AND   cat.id = c.categoria_id
                    AND   p.cedula = c.cedula_participan                  
                """
    params = {}

    if evento_id:
        query += " AND e.id = :evento_id"
        params["evento_id"] = evento_id       

    query += " ORDER BY e.id" 

    result = await db.execute(text(query), params)
    rows = result.mappings().all()

    return {"calificacionestot": rows}

# ==========================================================
# 1B. Listar calificaciones promedio (Ranking de ganadores)
# GET /api/calificacionestot
# ==========================================================
@router.get("/calificacionesranking")
async def listar_calificacionestot(evento_id: Optional[int] = Query(None), 
                                   db: AsyncSession = Depends(get_db)
):
    query = """
                SELECT
                c.id,
                e.id            AS evento_id,
                e.nombre        AS evento,
                cat.id          AS categoria_id,
                cat.categoria   AS categoria,
                p.cedula        AS cedula_participan,
                p.nombre        AS participante,
                c.promedio
                FROM calificaciones_promedio c, eventos e, categorias cat, participantes p
                WHERE e.id = c.evento_id
                AND   cat.id = c.categoria_id
                AND   p.cedula = c.cedula_participan                  
                """
    params = {}

    if evento_id:
        query += " AND e.id = :evento_id"
        params["evento_id"] = evento_id       

    query += " ORDER BY e.id, cat.id, c.promedio desc" 

    result = await db.execute(text(query), params)
    rows = result.mappings().all()

    return {"calificacionesranking": rows}


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

    query_existe = text("""
                        SELECT 1
                        FROM calificaciones
                        WHERE cedula_jurado = :cedula_jurado
                        AND   cedula_participan = :cedula_participan
                        AND   evento_id = :evento_id
                        AND   categoria_id = :categoria_id
                        LIMIT 1
                        """)
    result = await db.execute(query_existe, {
        "cedula_jurado": data.cedula_jurado,
        "cedula_participan": data.cedula_participan,
        "evento_id": data.evento_id,
        "categoria_id": data.categoria_id,
    })

    if result.first():
        raise HTTPException(
            status_code=409,
            detail="El participante ya tiene calificación para este evento y categoria"
        )


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
# 4. Actualizar calificación
# ============================================
@router.put("/calificaciones/{id}")
async def actualizar_calificacion(id: int, datos: dict, db: AsyncSession = Depends(get_db)):

    datos["id"] = id

    query = text("""
        UPDATE calificaciones
        SET puntaje = :puntaje,                        
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

  
    result = await db.execute(query, datos)
    categoria = result.mappings().first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")

    await db.commit()
    return categoria


# ============================================
# 5. Eliminar calificación
# ============================================
@router.delete("/calificaciones/{id}")
async def eliminar_calificacion(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM calificaciones WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    categoria = result.mappings().first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")

    await db.commit()
    return {"message": "calificación eliminada correctamente", "id": id}

# ====================================================
# 6. Consulta calificaciones promedio
# ====================================================
@router.get("/calificaciones-promedio/existen")
async def existen_promedios(db: AsyncSession = Depends(get_db)):
    query = text("SELECT COUNT(*) AS total FROM calificaciones_promedio")
    result = await db.execute(query)
    total = result.scalar()

    return {
        "existen": total > 0,
        "total": total
    }

# ====================================================
# 7. Calcula calificación promedio por participante
# ====================================================
@router.post("/calificaciones-promedio")
async def generar_calificaciones_promedio( db: AsyncSession = Depends(get_db)):    
    
    try:
        await db.execute(text("TRUNCATE TABLE calificaciones_promedio"))

        query = text("""
                        INSERT INTO calificaciones_promedio (                     
                            cedula_participan,                        
                            evento_id,
                            categoria_id,
                            promedio
                        )
                        SELECT                              
                            cedula_participan,                        
                            evento_id,
                            categoria_id,
                            ROUND(AVG(puntaje),2) AS promedio
                        FROM calificaciones
                        GROUP BY cedula_participan,                        
                                evento_id,
                                categoria_id                                        
                """)
            
        await db.execute(query) 
        await db.commit()
                
        return {"message": "Promedios insertados correctamente"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )