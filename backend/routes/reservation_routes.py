from flask import Blueprint
from controllers.reservation_controller import (
    reserve_book,
    return_book,
    get_user_books,
    get_borrowing_history,
    get_due_soon_reminders
)

reservation_bp = Blueprint('reservation', __name__)

# Reserve & return
reservation_bp.route('/reserve', methods=['POST'])(reserve_book)
reservation_bp.route('/return', methods=['POST'])(return_book)

# User-specific (now expect JSON { "email": ... })
reservation_bp.route('/my-books', methods=['POST'])(get_user_books)
reservation_bp.route('/history', methods=['POST'])(get_borrowing_history)

# General
reservation_bp.route('/due-reminders', methods=['GET'])(get_due_soon_reminders)
