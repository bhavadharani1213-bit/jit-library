from models import db
from datetime import datetime
from datetime import datetime, timedelta

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Reserved at
    status = db.Column(db.String(20), default="reserved")  # reserved, borrowed, returned
    borrowed_at = db.Column(db.DateTime, nullable=True)  # Added now
    returned_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=15))
    fine_amount = db.Column(db.Integer, default=0)
    reserved_date = db.Column(db.DateTime, default=datetime.utcnow)


