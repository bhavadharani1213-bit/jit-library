from models import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    publication = db.Column(db.String(100))
    department = db.Column(db.String(50))  # AIDS, CSE, IT, MECH, etc.
    category = db.Column(db.String(50))    # Textbook, Novel, Journal, E-book
    ebook_url = db.Column(db.String(300))  # For e-books only (view/download)
    ebook_pdf_link = db.Column(db.String(300))
    year_of_publication = db.Column(db.String(4))
    available_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservation_count = db.Column(db.Integer, default=0)


    def is_ebook(self):
        return self.category.lower() == "e-book"
