from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db import init_db,SessionLocal
from app.api.router import api_router
from app.services.sla import ensure_sla_rules
@asynccontextmanager
async def lifespan(app):
    init_db();db=SessionLocal()
    try: ensure_sla_rules(db)
    finally: db.close()
    yield
app=FastAPI(title=settings.app_name,version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(api_router)
@app.get('/')
def root(): return {'message':settings.app_name,'docs':'/docs','status':'ok'}
@app.get('/health')
def health(): return {'status':'healthy'}
