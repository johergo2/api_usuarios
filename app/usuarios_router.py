from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .database import SessionLocal

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("/usuarios")
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"usuarios": rows}


@router.get("/usuarios/{id}")
async def obtener_usuario(id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios WHERE id = :id")
    result = await db.execute(query, {"id": id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return row
