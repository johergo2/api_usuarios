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

# =======================================================
# 5. Obtener usuario y Rol
# =======================================================
@router.get("/usuario-rol")
async def obtener_rol_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = """
        SELECT rol
        FROM usuarios_eventos
        WHERE usuario_id = :usuario_id
    """
    result = await db.execute(text(query), {
        "usuario_id": usuario_id
    })
    row = result.first()

    if not row:
        return {"rol": None}

    return {"rol": row.rol}

# ============================================
# 6. Crear usuario
# ============================================
@router.post("/usuario")
async def crear_usuario(usuario: dict, db: AsyncSession = Depends(get_db)):

    print("📌 Crear un usuario en la tabla usuarios:", usuario)
    
    query = text("""
        INSERT INTO usuarios (nombre, email, contrasena, estado, rol)
        VALUES (:nombre, :email, :contrasena, :estado, :rol)
        RETURNING *;
    """)

    result = await db.execute(query, usuario)
    nuevo_usuario = result.mappings().first()
    await db.commit()

    return nuevo_usuario

# ============================================
# 7. Actualizar usuario
# ============================================
@router.put("/usuarios/{id}")
async def actualizar_usuario(id: int, datos: dict, db: AsyncSession = Depends(get_db)):

    datos["id"] = id

    query = text("""
        UPDATE usuarios
        SET nombre = :nombre,  
            email = :email,                       
            contrasena = :contrasena,                        
            estado = :estado,
            rol = :rol,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *;
    """)

  
    result = await db.execute(query, datos)
    usuario = result.mappings().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db.commit()
    return usuario

# ============================================
# 8. Eliminar usuario
# ============================================
@router.delete("/usuarios/{id}")
async def eliminar_usuarios(id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM usuarios WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": id})
    usuario = result.mappings().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db.commit()
    return {"message": "usuario eliminado correctamente", "id": id}
