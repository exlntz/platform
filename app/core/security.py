from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import timedelta,datetime,timezone

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "kirpich"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context=CryptContext(schemes=['argon2'])

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def is_password_correct(password: str, hashed_password_from_db: str) -> bool:
    return pwd_context.verify(password,hashed_password_from_db)

def create_access_token(data: dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt