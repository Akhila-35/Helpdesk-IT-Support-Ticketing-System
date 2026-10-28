from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import settings
class Base(DeclarativeBase): pass
args={'check_same_thread':False} if settings.database_url.startswith('sqlite') else {}
engine=create_engine(settings.database_url,connect_args=args)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
