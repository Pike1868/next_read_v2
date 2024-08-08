from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
import datetime

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            exp_timestamp = claims['exp']
            current_timestamp = datetime.datetime.timestamp(datetime.datetime.utcnow())
            
            if current_timestamp > exp_timestamp:
                return jsonify({"msg": "Session expired, Please sign in again."}), 401

        except Exception as e:
            return jsonify({"msg": "Token is missing or invalid"}), 401

        return f(*args, **kwargs)
    return decorated_function
