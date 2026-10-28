from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.core.security import hash_password,verify_password,create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest,LoginJSONRequest,TokenResponse,UserRead
router=APIRouter()
def authenticate(email,password,db):
    u=db.query(User).filter(User.email==email.lower()).first()
    if not u or not verify_password(password,u.password_hash): raise HTTPException(status_code=401,detail='Incorrect email or password',headers={'WWW-Authenticate':'Bearer'})
    if not u.is_active: raise HTTPException(status_code=403,detail='User account is inactive')
    return TokenResponse(access_token=create_access_token(u.id,u.role.value),user=u)
@router.post('/register',response_model=UserRead,status_code=201)
def register(data:RegisterRequest,db:Session=Depends(get_db)):
    email=str(data.email).lower()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(status_code=409,detail='Email is already registered')
    u=User(full_name=data.full_name.strip(),email=email,password_hash=hash_password(data.password)); db.add(u); db.commit(); db.refresh(u); return u
@router.post('/login',response_model=TokenResponse)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)): return authenticate(form.username,form.password,db)
@router.post('/login/json',response_model=TokenResponse)
def login_json(data:LoginJSONRequest,db:Session=Depends(get_db)): return authenticate(str(data.email),data.password,db)
