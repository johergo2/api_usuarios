from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

router = APIRouter()

# Obtener sesión de BD
async def get_db():
    async with SessionLocal() as session:
        yield session


# ============================================
# 1. Listar eventos
# ============================================
@router.get("/eventos")
async def listar_eventos(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM eventos ORDER BY id")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"eventos": rows}


# ============================================
# 2. Obtener evento por ID
# ============================================
@router.get("/eventos/{id}")
async def obtener_evento(id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM eventos WHERE id = :id")
    result = await db.execute(query, {"id": id})
    evento = result.mappings().first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    return evento


# ============================================
# 3. Crear evento
# ============================================
@router.post("/eventos")
async def crear_evento(evento: dict, db: AsyncSession = Depends(get_db)):
    query = text("""
        INSERT INTO eventos (nombre, descripcion, fecha_evento, fecha_fin, estado)
        VALUES (:nombre, :descripcion, :fecha_inicio, :fecha_fin, :estado)
        RETURNING *;
    """)

    result = await db.execute(query, evento)
    nuevo_evento = result.mappings().first()
    await db.commit()

    return nuevo_evento


# ============================================
# 4. Actualizar evento
# ============================================
@router.put("/eventos/{id}")
async def actualizar_evento(id: int, datos: dict, db: AsyncSession = Depends(get_db)):
    query = text("""
        UPDATE eventos
        SET nombre = :nombre,
            descripcion = :descripcion,
            fecha_inicio = :fecha_inicio,
            fecha_fin = :fecha_fin,
            estado = :estado,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

    datos["id"] = id
    result = await db.execute(query, datos)
    evento = result.mappings().first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    await db.commit()
    return evento


# ============================================
# 5. Eliminar evento
# ============================================
@router.delete("/eventos/{id}")
async def eliminar_evento(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM eventos WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    evento = result.mappings().first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    await db.commit()
    return {"message": "Evento eliminado correctamente", "id": id}
