from passlib.context import CryptContext

pwd_context=CryptContext(schemes=['bcrypt'])

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def is_password_correct(password: str, hashed_password_from_db: str) -> bool:
    return pwd_context.verify(password,hashed_password_from_db)

a=get_password_hash('привет')
print(a)
print(is_password_correct('привет',a))