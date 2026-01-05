from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal

router = APIRouter()

# ============================================
# Obtener sesión de BD
# ============================================
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/jurados-categorias-eventos")
async def listar_jurados(
    evento_id: int | None = None,
    cedula: str | None = None,
    usuario_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = """
        SELECT
            pce.id,
            pce.cedula,
            p.nombre AS jurado,
            pce.evento_id,
            e.nombre AS evento,
            pce.categoria_id,
            c.categoria,
            pce.fecha_creacion
        FROM jurados_categorias_eventos pce
        JOIN jurados p ON p.cedula = pce.cedula
        JOIN eventos e ON e.id = pce.evento_id
        JOIN categorias c ON c.id = pce.categoria_id
        JOIN usuarios_eventos ue ON ue.evento_id = e.id
        WHERE 1=1
    """

    params = {}

    if evento_id:
        query += " AND pce.evento_id = :evento_id"
        params["evento_id"] = evento_id

    if cedula:
        query += " AND pce.cedula = :cedula"
        params["cedula"] = cedula

    if usuario_id:
        query += " AND ue.usuario_id = :usuario_id"
        params["usuario_id"] = usuario_id        

    query += " ORDER BY pce.evento_id, pce.categoria_id, pce.cedula"

    result = await db.execute(text(query), params)
    rows = result.mappings().all()

    return {"data": rows}


@router.post("/jurados-categorias-eventos")
async def asignar_jurado_evento(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    cedula = data.get("cedula")
    evento_id = data.get("evento_id")
    categorias = data.get("categorias")

    if not cedula or not evento_id or not categorias:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar cedula, evento_id y lista de categorias"
        )

    insert_query = text("""
        INSERT INTO jurados_categorias_eventos
        (cedula, evento_id, categoria_id)
        VALUES (:cedula, :evento_id, :categoria_id)
        ON CONFLICT DO NOTHING
    """)

    for categoria_id in categorias:
        await db.execute(
            insert_query,
            {
                "cedula": cedula,
                "evento_id": evento_id,
                "categoria_id": categoria_id
            }
        )

    await db.commit()

    return {
        "message": "Jurado asignado correctamente",
        "cedula": cedula,
        "evento_id": evento_id,
        "categorias": categorias
    }

@router.get("/jurados/{cedula}/eventos/{evento_id}/categorias")
async def categorias_jurado_evento(
    cedula: str,
    evento_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            c.id,
            c.categoria
        FROM jurados_categorias_eventos pce
        JOIN categorias c ON c.id = pce.categoria_id
        WHERE pce.cedula = :cedula
          AND pce.evento_id = :evento_id
        ORDER BY c.categoria
    """)

    result = await db.execute(
        query,
        {"cedula": cedula, "evento_id": evento_id}
    )

    categorias = result.mappings().all()

    return {
        "cedula": cedula,
        "evento_id": evento_id,
        "categorias": categorias
    }

@router.delete(
    "/jurados/{cedula}/eventos/{evento_id}/categorias/{categoria_id}"
)
async def eliminar_categoria_jurado(
    cedula: str,
    evento_id: int,
    categoria_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        DELETE FROM jurados_categorias_eventos
        WHERE cedula = :cedula
          AND evento_id = :evento_id
          AND categoria_id = :categoria_id
        RETURNING id
    """)

    result = await db.execute(
        query,
        {
            "cedula": cedula,
            "evento_id": evento_id,
            "categoria_id": categoria_id
        }
    )

    eliminado = result.first()

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="La asignación no existe"
        )

    await db.commit()

    return {
        "message": "Categoría eliminada del jurado",
        "cedula": cedula,
        "evento_id": evento_id,
        "categoria_id": categoria_id
    }

@router.delete("/jurados/{cedula}/eventos/{evento_id}")
async def eliminar_jurado_evento(
    cedula: str,
    evento_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        DELETE FROM jurados_categ_eventos
        WHERE cedula = :cedula
          AND evento_id = :evento_id
        RETURNING id
    """)

    result = await db.execute(
        query,
        {"cedula": cedula, "evento_id": evento_id}
    )

    eliminados = result.fetchall()

    if not eliminados:
        raise HTTPException(
            status_code=404,
            detail="El jurado no tiene categorías en este evento"
        )

    await db.commit()

    return {
        "message": "Jurado eliminado del evento",
        "total_categorias": len(eliminados)
    }

