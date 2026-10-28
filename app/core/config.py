from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name:str='Helpdesk / IT Support Ticketing System'
    database_url:str='sqlite:///./helpdesk.db'
    jwt_secret_key:str='CHANGE_THIS_IN_PRODUCTION_TO_A_LONG_RANDOM_SECRET'
    jwt_algorithm:str='HS256'
    access_token_expire_minutes:int=60
    cors_origins:list[str]=['*']
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
