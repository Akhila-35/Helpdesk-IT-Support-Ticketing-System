from app.models.notification import Notification
def notify(db,user_id,title,message,ticket_id=None):
    n=Notification(user_id=user_id,ticket_id=ticket_id,title=title,message=message); db.add(n); return n
