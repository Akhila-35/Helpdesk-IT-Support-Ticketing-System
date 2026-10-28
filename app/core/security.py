from datetime import datetime,timedelta,timezone
import jwt
from fastapi import HTTPException,status
from pwdlib import PasswordHash
from app.core.config import settings
password_hash=PasswordHash.recommended()
def hash_password(password): return password_hash.hash(password)
def verify_password(password,hashed): return password_hash.verify(password,hashed)
def create_access_token(subject,role):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({'sub':str(subject),'role':role,'exp':exp},settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
def decode_access_token(token):
    err=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid or expired authentication token',headers={'WWW-Authenticate':'Bearer'})
    try: payload=jwt.decode(token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as e: raise err from e
    if not payload.get('sub'): raise err
    return payload
