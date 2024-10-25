import logging
from fastapi.security import OAuth2PasswordBearer

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Autor: Jose E Moraes

# Criação do esquema de autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger.debug("OAuth2PasswordBearer criado com tokenUrl='token'.")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependência para obter o usuário atual a partir do token de autenticação.

    Parameters:
    - token (str): O token de autenticação fornecido pelo cliente.

    Returns:
    - User: O usuário autenticado (a ser implementado).

    Raises:
    - HTTPException: Se o token não for válido ou o usuário não for encontrado.
    """
    logger.debug(f"Obtendo o usuário atual com o token: {token}")
    # Implementar a lógica para verificar o token e retornar o usuário
    # Exemplo: user = verify_token(token)
    # if not user:
    #     logger.error("Token inválido ou usuário não encontrado.")
    #     raise HTTPException(status_code=401, detail="Token inválido.")
    # return user