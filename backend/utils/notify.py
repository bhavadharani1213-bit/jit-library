from models.notification import Notification
from models import db

def create_notification(user_id, message):
    note = Notification(user_id=user_id, message=message)
    db.session.add(note)
    db.session.commit()
