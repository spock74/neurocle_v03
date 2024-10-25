import logging
from sqlalchemy import Column, Integer, String
from app.core.db import Base

# Este módulo define o modelo de Item para a tabela 'items' no banco de dados.
# Ele inclui atributos como id, name e description, além de métodos para inicialização e representação do objeto.

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Autor: Jose E Moraes

class Item(Base):
    """
    Modelo de Item para a tabela 'items'.

    Atributos:
        id (int): Identificador único do item.
        name (str): Nome do item.
        description (str): Descrição do item.
    """
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    def __init__(self, name: str, description: str):
        """
        Inicializa um novo Item.

        Parameters:
        - name (str): Nome do item.
        - description (str): Descrição do item.
        """
        self.name = name
        self.description = description
        logger.debug("Item criado: %s", self)

    def __repr__(self):
        return f"<Item(id={self.id}, name={self.name}, description={self.description})>"