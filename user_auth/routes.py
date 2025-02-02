from flask import Blueprint, request
from user_auth.use_cases import handle_register, handle_login

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return handle_register(data)

@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return handle_login(data)
