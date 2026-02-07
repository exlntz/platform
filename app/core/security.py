from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import timedelta,datetime,timezone
from app.core.config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context=CryptContext(schemes=['argon2'],deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def is_password_correct(password: str, hashed_password_from_db: str) -> bool:
    return pwd_context.verify(password,hashed_password_from_db)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire,"iat": datetime.now(timezone.utc)})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt