from flask import Blueprint
from controllers import book_request_controller as brc

book_request_bp = Blueprint('book_request', __name__)

# Submit new request
book_request_bp.route('/submit', methods=['POST'])(brc.submit_request)

# Approve or reject request
book_request_bp.route('/update-status', methods=['POST'])(brc.update_request_status)

# Get requests of a specific user
book_request_bp.route('/my-requests', methods=['GET'])(brc.get_user_requests)

# Get all requests (admin only)
book_request_bp.route('/all', methods=['GET'])(brc.get_all_requests)
