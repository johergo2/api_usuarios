from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from datetime import datetime, date

router = APIRouter()

# Obtener sesión de BD
async def get_db():
    async with SessionLocal() as session:
        yield session


# ============================================
# 1. Listar participantes
# ============================================
@router.get("/participantes")
async def listar_participantes(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM participantes ORDER BY id")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"participantes": rows}


# ============================================
# 2. Obtener participante por ID
# ============================================
@router.get("/participantes/{id}")
async def obtener_participante(id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM participantes WHERE id = :id")
    result = await db.execute(query, {"id": id})
    participante = result.mappings().first()

    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    return participante


# ============================================
# 3. Crear participante
# ============================================
@router.post("/participantes")
async def crear_participante(participante: dict, db: AsyncSession = Depends(get_db)):

    print("📌 Datos recibidos en crear_participante:", participante)
    
    query = text("""
        INSERT INTO participantes (cedula, nombre, tipo, observacion)
        VALUES (:cedula, :nombre, :tipo, :observacion)
        RETURNING *;
    """)

    result = await db.execute(query, participante)
    nuevo_participante = result.mappings().first()
    await db.commit()

    return nuevo_participante


# ============================================
# 4. Actualizar participante
# ============================================
@router.put("/participantes/{id}")
async def actualizar_participante(id: int, datos: dict, db: AsyncSession = Depends(get_db)):

    datos["id"] = id

    query = text("""
        UPDATE participantes
        SET cedula = :cedula,
            nombre = :nombre,   
            tipo = :tipo,        
            observacion = :observacion,                        
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

  
    result = await db.execute(query, datos)
    participante = result.mappings().first()

    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    await db.commit()
    return participante


# ============================================
# 5. Eliminar participante
# ============================================
@router.delete("/participantes/{id}")
async def eliminar_participante(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM participantes WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    participante = result.mappings().first()

    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    await db.commit()
    return {"message": "participante eliminado correctamente", "id": id}
