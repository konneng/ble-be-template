
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "ble_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_PASSWORD_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    return _create_token(data, ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(data: dict):
    return _create_token(data, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60)

def create_reset_token(data: dict):
    return _create_token(data, RESET_PASSWORD_EXPIRE_MINUTES)

def _create_token(data: dict, expires_minutes: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
