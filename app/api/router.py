from fastapi import APIRouter
from app.api.routes import auth,users,categories,tickets,notifications
api_router=APIRouter()
api_router.include_router(auth.router,prefix='/auth',tags=['Authentication'])
api_router.include_router(users.router,prefix='/users',tags=['Users'])
api_router.include_router(categories.router,prefix='/categories',tags=['Categories'])
api_router.include_router(tickets.router,prefix='/tickets',tags=['Tickets'])
api_router.include_router(notifications.router,prefix='/notifications',tags=['Notifications'])
