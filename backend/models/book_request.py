from models import db
from datetime import datetime

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)  # new column
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=True)
    reason = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
