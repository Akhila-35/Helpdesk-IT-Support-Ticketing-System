from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.dependencies import get_current_user,get_db,require_roles
from app.models.category import TicketCategory
from app.schemas.ticket import CategoryCreate,CategoryRead
router=APIRouter()
@router.get('',response_model=list[CategoryRead])
def list_categories(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(TicketCategory).filter(TicketCategory.is_active.is_(True)).order_by(TicketCategory.name).all()
@router.post('',response_model=CategoryRead,status_code=201)
def create(data:CategoryCreate,db:Session=Depends(get_db),_=Depends(require_roles('admin'))):
    c=TicketCategory(name=data.name.strip(),description=data.description); db.add(c)
    try: db.commit()
    except IntegrityError as e: db.rollback(); raise HTTPException(status_code=409,detail='Category name already exists') from e
    db.refresh(c); return c
