from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class EventoCategoria(Base):
    __tablename__ = "eventos_categorias"

    id = Column(Integer, primary_key=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
