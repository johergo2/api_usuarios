from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

router = APIRouter()

# Obtener sesión de BD
async def get_db():
    async with SessionLocal() as session:
        yield session


# =======================================================
# 1. Obtener todos los usuarios
# =======================================================
@router.get("/usuarios")
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM usuarios ORDER BY id")
    result = await db.execute(query)
    rows = result.mappings().all()
    return {"usuarios": rows}


# =======================================================
# 2. Obtener usuario por ID
# =======================================================
@router.get("/usuarios/{id}")
async def obtener_usuario(id: int, db: AsyncSession = Depends(get_db)):
    query = text("""SELECT * FROM usuarios WHERE id = :id AND estado = 'ACT'""" )
    result = await db.execute(query, {"id": id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Usuario con id no encontrado o inactivo")

    return row


# =======================================================
# 3. Obtener usuario por nombre (coincidencia exacta)
# =======================================================
@router.get("/usuarios/nombre/{nombre}")
async def obtener_usuario_por_nombre(nombre: str, db: AsyncSession = Depends(get_db)):
    query = text("""SELECT * FROM usuarios WHERE nombre = :nombre AND estado = 'ACT'""")
    result = await db.execute(query, {"nombre": nombre})
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un usuario activo con el nombre '{nombre}'",
        )

    return row


# =======================================================
# 4. Login por nombre y contraseña
# =======================================================
@router.post("/usuarios/login")
async def login(datos: dict, db: AsyncSession = Depends(get_db)):
    nombre = datos.get("nombre")
    contrasena = datos.get("contrasena")

    if not nombre or not contrasena:
        raise HTTPException(
            status_code=400,
            detail="Nombre y contraseña son obligatorios"
        )

    query = text("""SELECT * FROM usuarios WHERE nombre = :nombre AND estado = 'ACT'""")
    result = await db.execute(query, {"nombre": nombre})
    usuario = result.mappings().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe o está inactivo")

    if usuario["contrasena"] != contrasena:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {
        "message": "Acceso concedido",
        "usuario": usuario
    }
