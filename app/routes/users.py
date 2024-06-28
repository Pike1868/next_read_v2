from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from ..models import User, db
from datetime import datetime

users_bp = Blueprint('users_bp', __name__, url_prefix='/users')

TOP_GENRES = ["Romance", "Dystopian", "Mystery", "Fantasy", "Science Fiction", "Thriller"]

@users_bp.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "Email already registered"}), 400

    new_user = User(
        username=username,
        email=email,
        password=User.hash_password(password)
    )
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)

    return jsonify(access_token=access_token), 201

@users_bp.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid credentials"}), 401

@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(username=user.username, email=user.email, bio=user.bio, location=user.location, image_url=user.image_url), 200

@users_bp.route("/profile/edit", methods=["POST"])
@jwt_required()
def edit_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    if user.check_password(data.get('password')):
        user.username = data.get('username')
        user.email = data.get('email')
        user.bio = data.get('bio')
        user.location = data.get('location')
        user.image_url = data.get('image_url')
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"msg": "Profile updated successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Username or email already taken"}), 400
    else:
        return jsonify({"msg": "Incorrect password"}), 401

@users_bp.route("/sign_out", methods=["POST"])
@jwt_required()
def sign_out():
    return jsonify({"msg": "Successfully signed out"}), 200

@users_bp.route("/delete", methods=["POST"])
@jwt_required()
def delete_user_account():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "Your account has been deleted."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting account. Please try again."}), 500
