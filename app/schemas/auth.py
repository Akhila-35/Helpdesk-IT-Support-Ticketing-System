from pydantic import BaseModel,ConfigDict,EmailStr,Field
from app.schemas.enums import UserRole
class RegisterRequest(BaseModel): full_name:str=Field(min_length=2,max_length=120); email:EmailStr; password:str=Field(min_length=8,max_length=128)
class LoginJSONRequest(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class UserRead(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; full_name:str; email:EmailStr; role:UserRole; is_active:bool
class TokenResponse(BaseModel): access_token:str; token_type:str='bearer'; user:UserRead
