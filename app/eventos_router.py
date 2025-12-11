from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from datetime import datetime

router = APIRouter()

# Obtener sesión de BD
async def get_db():
    async with SessionLocal() as session:
        yield session

def normalizar_fecha(fecha):
    """Convierte una fecha DD/MM/YYYY o '' a YYYY-MM-DD o None."""
    if not fecha or fecha == "":
        return None

    # Si ya viene en formato YYYY-MM-DD, retornar directo
    if len(fecha) == 10 and fecha[4] == '-' and fecha[7] == '-':
        return fecha

    # Si viene en DD/MM/YYYY, convertir
    try:
        dia, mes, anio = fecha.split("/")
        return f"{anio}-{mes}-{dia}"
    except:
        return None


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
    # Convertir fecha_evento del formato DD/MM/YYYY a YYYY-MM-DD si viene así
    evento["fecha_evento"] = normalizar_fecha(evento.get("fecha_evento"))

    query = text("""
        INSERT INTO eventos (nombre, descripcion, fecha_evento, lugar, estado)
        VALUES (:nombre, :descripcion, :fecha_evento, :lugar, :estado)
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

    datos["fecha_evento"] = normalizar_fecha(datos.get("fecha_evento"))
    datos["id"] = id

    query = text("""
        UPDATE eventos
        SET nombre = :nombre,
            descripcion = :descripcion,   
            fecha_evento = :fecha_evento         
            lugar = :lugar,            
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
