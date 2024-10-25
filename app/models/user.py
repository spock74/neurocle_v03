import logging
from sqlalchemy import Column, Integer, String
from app.core.db import Base

# Este módulo define o modelo de User para a tabela 'users' no banco de dados.
# Ele inclui atributos como id, username, email e hashed_password, 
# além de métodos para inicialização e representação do objeto.

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Autor: Jose E Moraes

class User(Base):
    """
    Modelo de User para a tabela 'users'.

    Atributos:
        id (int): Identificador único do usuário.
        username (str): Nome de usuário.
        email (str): Endereço de e-mail do usuário.
        hashed_password (str): Senha do usuário, armazenada de forma segura.
    """
    __tablename__ = "users"
    
    # id = Column(Integer, primary_key=True, index=True)
    # username = Column(String, unique=True, index=True, nullable=False)
    # email = Column(String, unique=True, index=True, nullable=False)
    # hashed_password = Column(String, nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String)
    fusername = Column(String)
    
    
    def __init__(self, username: str, email: str, hashed_password: str):
        """
        Inicializa um novo User.

        Parameters:
        - username (str): Nome de usuário.
        - email (str): Endereço de e-mail do usuário.
        - hashed_password (str): Senha do usuário, armazenada de forma segura.
        """
        try:
            self.username = username
            self.email = email
            self.hashed_password = hashed_password
            logger.debug("User criado: %s", self)
        except Exception as e:
            logger.error("Erro ao criar User: %s", e)
            raise

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"