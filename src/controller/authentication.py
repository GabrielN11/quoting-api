from flask_restx import Resource
from datetime import datetime, timedelta
import jwt

from src.server.instance import api, bcrypt, db
from src.models.user import User
from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY

@api.route('/sign-up')
class SignUpRoute(Resource):
    def post(self):
        data = api.payload
        username = None
        password = None

        try:
            username = data['username']
            password = data['password']
        except:
            return {"error": "Missing data."}, 400

        if(len(password) < 6):
            return {"error": "Password is too short."}, 400

        if(User.query.filter_by(username=username).first() != None):
            return {"error": "Username already exists"}, 400

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            user = User(username=username, password=hashed_pw)
            db.session.add(user)
            db.session.commit()

            token = jwt.encode({"id": user.id, 'admin': False, 'exp': datetime.utcnow() + timedelta(minutes=5)}, JWT_KEY, algorithm="HS256")
            
            data = {
                "id": user.id,
                "username": username,
                "name": user.name,
                "is_admin": user.admin,
                "token": token
            }

            return {"message": "User created.", "data": data}, 201
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/sign-in')
class SignInRoute(Resource):
    def post(self):
        data = api.payload
        username = None
        password = None

        try:
            username = data['username']
            password = data['password']
        except:
            return {"error": "Missing data"}, 400

        userData = User.query.filter_by(username=username).first()

        if userData == None:
            return {"error": "Invalid authentication."}, 400

        if bcrypt.check_password_hash(userData.password, password):
            token = jwt.encode({"id": userData.id, 'admin': userData.admin, 'exp': datetime.utcnow() + timedelta(minutes=5)}, JWT_KEY, algorithm="HS256")

            user = {
                "id": userData.id,
                "username": username,
                "name": userData.name,
                "is_admin": userData.admin,
                "token": token
            }

            return {"message": "Successfully authenticated", "data": user}, 200
        else:
            return {"error": "Invalid authentication."}, 400