# app/api/api_v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.user import UserUpdate  
from app.core.settings.conf import logger
from app.api.dependencies import get_db_session, db_dependency


# # Configuração do logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = db_dependency):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving user")


@router.get("/users")
def read_users(db: Session = db_dependency):
    try:
        # Use 'db' para fazer consultas
        users = db.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Erro ao obter usuários: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter usuários")


@router.post("/users", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = db_dependency):
    try:
        # Create a new User object without hashing the password
        new_user = User(
            email=user.email,
            hashed_password=user.password,  # CAUTION: Storing plain password for testing
            full_name=user.full_name
        )
        
        # Add the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Return the created user
        return UserCreate(email=new_user.email, password=user.password, full_name=new_user.full_name)
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")  # For debugging
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")





@router.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserCreate, db: Session = db_dependency):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error updating user: {str(e)}")


@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = db_dependency):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error deleting user: {str(e)}")
