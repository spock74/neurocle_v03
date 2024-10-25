import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.item import Item
from app.schemas.item import ItemCreate, Item as ItemSchema
from app.api.dependencies import get_db_session
from app.core.settings.conf import logger
# # Configuração do logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Autor: Jose E Moraes

router = APIRouter()

@router.get("/items", response_model=List[ItemSchema])
def get_items(db: Session = Depends(get_db_session)):
    """
    Recupera todos os itens do banco de dados.

    Parameters:
    - db (Session): A sessão do banco de dados.

    Returns:
    - List[ItemSchema]: Uma lista de itens.
    """
    logger.debug("Recuperando todos os itens do banco de dados.")
    items = db.query(Item).all()
    logger.debug(f"Itens recuperados: {items}")
    return items


@router.post("/items", response_model=ItemSchema)
def create_item(item: ItemCreate, db: Session = Depends(get_db_session)):
    """
    Cria um novo item no banco de dados.

    Parameters:
    - item (ItemCreate): O item a ser criado.
    - db (Session): A sessão do banco de dados.

    Returns:
    - ItemSchema: O item criado.

    Raises:
    - HTTPException: Se ocorrer um erro ao criar o item.
    """
    logger.debug(f"Criando um novo item: {item}")
    db_item = Item(name=item.name, description=item.description)
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.debug(f"Item criado com sucesso: {db_item}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar item: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar item.")
    
    return db_item


@router.put("/items/{item_id}", response_model=ItemSchema)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db_session)):
    """
    Atualiza um item existente no banco de dados.

    Parameters:
    - item_id (int): O ID do item a ser atualizado.
    - item (ItemCreate): Os novos dados do item.
    - db (Session): A sessão do banco de dados.

    Returns:
    - ItemSchema: O item atualizado.

    Raises:
    - HTTPException: Se o item não for encontrado ou se ocorrer um erro ao atualizar.
    """
    logger.debug(f"Atualizando item com ID {item_id}: {item}")
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        logger.error(f"Item com ID {item_id} não encontrado")
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    try:
        db_item.name = item.name
        db_item.description = item.description
        db.commit()
        db.refresh(db_item)
        logger.debug(f"Item atualizado com sucesso: {db_item}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar item: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar item")
    
    return db_item

@router.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int, db: Session = Depends(get_db_session)):
    """
    Remove um item do banco de dados.

    Parameters:
    - item_id (int): O ID do item a ser removido.
    - db (Session): A sessão do banco de dados.

    Returns:
    - dict: Uma mensagem de confirmação.

    Raises:
    - HTTPException: Se o item não for encontrado ou se ocorrer um erro ao remover.
    """
    logger.debug(f"Removendo item com ID {item_id}")
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        logger.error(f"Item com ID {item_id} não encontrado")
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    try:
        db.delete(db_item)
        db.commit()
        logger.debug(f"Item removido com sucesso: {db_item}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao remover item: {e}")
        raise HTTPException(status_code=500, detail="Erro ao remover item")
    
    return {"message": "Item removido com sucesso"}



