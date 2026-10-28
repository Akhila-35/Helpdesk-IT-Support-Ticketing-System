from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user,get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationRead
router=APIRouter()
@router.get('',response_model=list[NotificationRead])
def list_notifications(unread_only:bool=False,db:Session=Depends(get_db),user=Depends(get_current_user)):
    q=db.query(Notification).filter(Notification.user_id==user.id)
    if unread_only:q=q.filter(Notification.is_read.is_(False))
    return q.order_by(Notification.created_at.desc()).all()
@router.post('/{notification_id}/read',response_model=NotificationRead)
def read(notification_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    n=db.get(Notification,notification_id)
    if not n or n.user_id!=user.id: raise HTTPException(status_code=404,detail='Notification not found')
    n.is_read=True; db.commit(); db.refresh(n); return n
