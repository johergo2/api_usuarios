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
# 1. Listar jurados
# ============================================
@router.get("/jurados")
async def listar_participantes(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM jurados ORDER BY id")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"jurados": rows}


# ============================================
# 2. Obtener jurados por ID
# ============================================
@router.get("/jurados/{id}")
async def obtener_jurado(id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM jurado WHERE id = :id")
    result = await db.execute(query, {"id": id})
    jurado = result.mappings().first()

    if not jurado:
        raise HTTPException(status_code=404, detail="Jurado no encontrado")

    return jurado


# ============================================
# 3. Crear jurado
# ============================================
@router.post("/jurados")
async def crear_jurado(jurado: dict, db: AsyncSession = Depends(get_db)):

    print("📌 Datos recibidos en crear_jurado:", jurado)
    
    query = text("""
        INSERT INTO jurados (cedula, nombre, observacion)
        VALUES (:cedula, :nombre, :observacion)
        RETURNING *;
    """)

    result = await db.execute(query, jurado)
    nuevo_jurado = result.mappings().first()
    await db.commit()

    return nuevo_jurado


# ============================================
# 4. Actualizar jurado
# ============================================
@router.put("/jurados/{id}")
async def actualizar_jurado(id: int, datos: dict, db: AsyncSession = Depends(get_db)):

    datos["id"] = id

    query = text("""
        UPDATE jurados
        SET cedula = :cedula,
            nombre = :nombre,                       
            observacion = :observacion,                        
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

  
    result = await db.execute(query, datos)
    jurado = result.mappings().first()

    if not jurado:
        raise HTTPException(status_code=404, detail="Jurado no encontrado")

    await db.commit()
    return jurado


# ============================================
# 5. Eliminar jurado
# ============================================
@router.delete("/jurados/{id}")
async def eliminar_jurado(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM jurados WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    jurado = result.mappings().first()

    if not jurado:
        raise HTTPException(status_code=404, detail="Jurado no encontrado")

    await db.commit()
    return {"message": "jurado eliminado correctamente", "id": id}
