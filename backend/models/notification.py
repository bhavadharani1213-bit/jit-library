from models import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"   # good practice to name table explicitly

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="general")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # already enough
    seen = db.Column(db.Boolean, default=False)