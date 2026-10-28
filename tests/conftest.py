import os
os.environ['DATABASE_URL']='sqlite:///./test.db';os.environ['JWT_SECRET_KEY']='test-secret-key-123456789'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.main import app
from app.core.dependencies import get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.category import TicketCategory
from app.schemas.enums import UserRole
engine=create_engine('sqlite:///./test.db',connect_args={'check_same_thread':False});TestingSessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
@pytest.fixture(autouse=True)
def db_reset():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);db=TestingSessionLocal();db.add_all([TicketCategory(name='Hardware'),User(full_name='Admin',email='admin@example.com',password_hash=hash_password('AdminPass123!'),role=UserRole.ADMIN),User(full_name='Engineer',email='engineer@example.com',password_hash=hash_password('EngineerPass123!'),role=UserRole.ENGINEER),User(full_name='Requester',email='requester@example.com',password_hash=hash_password('RequesterPass123!'),role=UserRole.REQUESTER)]);db.commit();db.close();yield;Base.metadata.drop_all(engine)
@pytest.fixture
def client():
    def override():
        db=TestingSessionLocal()
        try:yield db
        finally:db.close()
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c:yield c
    app.dependency_overrides.clear()
