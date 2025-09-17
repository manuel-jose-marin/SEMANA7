from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .declarative_base import Base

class Receta(Base):
    __tablename__ = 'recetas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    tiempo_preparacion = Column(String, nullable=False)
    numero_personas = Column(Integer, nullable=False)
    calorias_porcion = Column(Integer, nullable=True)
    preparacion = Column(String, nullable=False)

    ingredientes = relationship("IngredienteReceta", back_populates="receta")
