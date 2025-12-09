from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

# ==============================
# 1. Obtener todos los usuarios
# ==============================
@router.get("/usuarios")
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios order by id")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"usuarios": rows}

# ==============================
# 2. Obtener un usuario por ID
# ==============================
@router.get("/usuarios/{id}")
async def obtener_usuario(id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios WHERE id = :id")
    result = await db.execute(query, {"id": id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario con id no encontrado")
    return row

# ============================================
# 2. Obtener usuario por nombre (coincidencia exacta)
# ============================================
@router.get("/usuarios/nombre/{nombre}")
async def obtener_usuario_por_nombre(nombre: str, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios WHERE nombre = :nombre")
    result = await db.execute(query, {"nombre": nombre})
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un usuario con el nombre '{nombre}'"
        )

    return row