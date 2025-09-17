from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .declarative_base import Base

class IngredienteReceta(Base):
    __tablename__ = 'ingrediente_receta'

    id = Column(Integer, primary_key=True)
    receta_id = Column(Integer, ForeignKey('recetas.id'), nullable=False)
    ingrediente_id = Column(Integer, ForeignKey('ingredientes.id'), nullable=False)
    cantidad = Column(String, nullable=False)

    # Relationships
    receta = relationship("Receta", back_populates="ingredientes")
    ingrediente = relationship("Ingrediente", back_populates="recetas")
