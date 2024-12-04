# app/core/db.py

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings.conf import logger
from sqlalchemy.orm import declarative_base

# Base declarativa para modelos
Base = declarative_base()

# URL de conexão com o banco de dados
## ********************************************************************************
DATABASE_URL = "postgresql+psycopg2://postgres:12345678@localhost:5432/neurocurso"
# ----- ALTERAR ===============:> 'LOCALHOST' PARA 'db' quando em produção (docker)
# DATABASE_URL = "postgresql+psycopg2://postgres:12345678@db:5432/neurocurso"
## ********************************************************************************


# import redis
# from app.core.settings.conf import Settings

# redis_client = redis.StrictRedis(host=Settings.REDIS_HOST, port=Settings.REDIS_PORT, db=0, decode_responses=True)

# ---------------------------------------------------------------------------------
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica a conexão antes de usar
        pool_recycle=3600,   # Recicla conexões após 1 hora
    )
    logger.debug("Engine criado com DATABASE_URL: %s", DATABASE_URL)
except Exception as e:
    logger.error("Erro ao criar o engine: %s", str(e))
    raise
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# Criação da fábrica de sessões
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.debug("SessionLocal criada.")
except Exception as e:
    logger.error("Erro ao criar SessionLocal: %s", str(e))
    raise
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
def get_db():
    """
    Gera uma nova sessão de banco de dados.

    Yields:
        Session: A sessão do banco de dados.

    Raises:
        Exception: Se ocorrer um erro ao obter a sessão do banco de dados.
    """
    logger.debug("Iniciando a sessão do banco de dados.")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Erro ao obter a sessão do banco de dados: %s", str(e))
        db.rollback()  # Garante que qualquer transação aberta seja revertida
        raise
    finally:
        logger.debug("Fechando a sessão do banco de dados.")
        db.close()
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# Função para criar todas as tabelas definidas
def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas no banco de dados.")
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# Função para dropar todas as tabelas (use com cautela!)
def drop_tables():
# ---------------------------------------------------------------------------------
    Base.metadata.drop_all(bind=engine)
    logger.warning("Todas as tabelas foram removidas do banco de dados.")
# ---------------------------------------------------------------------------------




if __name__ == "__main__":
    # Isso permite que você execute este script diretamente para criar ou dropar tabelas
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            create_tables()
        elif sys.argv[1] == "drop":
            drop_tables()
        else:
            print("Uso: python db.py [create|drop]")
    else:
        print("Uso: python db.py [create|drop]")

