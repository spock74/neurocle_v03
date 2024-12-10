from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user
)
from app.api.api_v1.assistants_schema import UserCreate, Token
from app.db.cruds_operations import create_user, get_user_by_email
from app.core.settings.conf import settings
from app.core.settings.conf import logger
import sqlite3
import os


router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        # Log da tentativa de login
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Buscar usuário
        user = get_user_by_email(form_data.username)
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar senha
        if not verify_password(form_data.password, user['hashed_password']):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token de acesso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {form_data.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/users", response_model=dict)
async def create_new_user(user: UserCreate) -> Any:
    """
    Create new user.
    """
    try:
        # Verificar se usuário já existe
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash da senha
        hashed_password = get_password_hash(user.password)
        
        # Criar usuário
        new_user = create_user(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        
        logger.info(f"User created successfully: {user.email}")
        return {
            "message": "User created successfully",
            "username": user.username,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.get("/users/me")
async def read_users_me(
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    try:
        user = get_user_by_email(current_user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return {
            "username": user['username'],
            "email": user['email']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )

# Endpoint opcional para debug (remover em produção)
@router.get("/debug/users/{email}")
async def debug_get_user(email: str):
    """
    DEBUG ONLY: Get user info and database status
    """
    debug_info = {
        "email_checked": email,
        "database_info": {},
        "user_info": None,
        "errors": []
    }
    
    try:
        # 1. Verificar se o arquivo do banco existe
        db_path = 'neurocle_v03.db'
        debug_info["database_info"]["db_exists"] = os.path.exists(db_path)
        debug_info["database_info"]["db_path"] = os.path.abspath(db_path)
        
        if not debug_info["database_info"]["db_exists"]:
            debug_info["errors"].append("Database file does not exist")
            return debug_info
            
        # 2. Tentar conectar ao banco
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 3. Verificar versão do SQLite
            cursor.execute("SELECT sqlite_version()")
            debug_info["database_info"]["sqlite_version"] = cursor.fetchone()[0]
            
            # 4. Verificar se a tabela existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            table_exists = cursor.fetchone() is not None
            debug_info["database_info"]["users_table_exists"] = table_exists
            
            if not table_exists:
                debug_info["errors"].append("Users table does not exist")
                return debug_info
            
            # 5. Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            debug_info["database_info"]["table_structure"] = [
                {"name": col[1], "type": col[2]} for col in columns
            ]
            
            # 6. Buscar usuário
            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = ?", 
                (email,)
            )
            user = cursor.fetchone()
            
            if user:
                debug_info["user_info"] = {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2]
                }
            else:
                debug_info["user_info"] = None
                debug_info["message"] = f"No user found with email: {email}"
            
        except sqlite3.Error as sql_e:
            debug_info["errors"].append(f"SQLite error: {str(sql_e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        debug_info["errors"].append(f"Unexpected error: {str(e)}")
        return debug_info