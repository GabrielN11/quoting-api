from functools import wraps
from flask import request
import jwt

from env import JWT_KEY
from src.server.instance import server

api = server.api

def adminAuthorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if not authorization:
            return 'Forbidden.', 403

        token = authorization.split()[1]
        try:
            data = jwt.decode(token, JWT_KEY, algorithms="HS256")

            if data and (not data['id'] or not data['admin']):
                return 'Forbidden.', 403
        except Exception as err:
            return 'Forbidden', 403

        return f(*args, **kwargs)

    return decorated