from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from .declarative_base import Base

class Ingrediente(Base):
    __tablename__ = 'ingredientes'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    unidad_medida = Column(String, nullable=False)
    valor_unidad = Column(Integer, nullable=False)
    sitio_compra = Column(String, nullable=False)
    
    recetas = relationship("IngredienteReceta", back_populates="ingrediente")
