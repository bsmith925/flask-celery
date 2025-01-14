from flask import Blueprint, request, jsonify
from apifairy.decorators import other_responses, body, response
from api import db
from api.models import User
from api.schemas import UserSchema

users = Blueprint('users', __name__)

@users.route('/users', methods=['POST'])
@body(UserSchema)
@response(UserSchema)
def create_user(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user

@users.route('/users/<int:id>', methods=['GET'])
@response(UserSchema)
def get_user(id):
    user = db.session.get(User, id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return user

@users.route('/users/<int:id>', methods=['PUT'])
@body(UserSchema)
@response(UserSchema)
def update_user(id, data):
    user = db.session.get(User, id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    user.update(data)
    db.session.commit()
    return user

@users.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return '', 204