from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db import SessionLocal
from app.models.user import User
scheme=HTTPBearer()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(scheme),db:Session=Depends(get_db)):
    payload=decode_access_token(credentials.credentials)
    try: uid=int(payload['sub'])
    except (KeyError,TypeError,ValueError) as e: raise HTTPException(status_code=401,detail='Invalid authentication token',headers={'WWW-Authenticate':'Bearer'}) from e
    user=db.get(User,uid)
    if not user or not user.is_active: raise HTTPException(status_code=401,detail='User is inactive or does not exist',headers={'WWW-Authenticate':'Bearer'})
    return user
def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user.role.value not in roles: raise HTTPException(status_code=403,detail='Insufficient permissions')
        return user
    return dep
