from flask import request
from flask_restx import Resource
from flask_mail import Message
from datetime import datetime, timedelta
import jwt
import random
import string

from src.server.instance import api, bcrypt, db, mail
from src.models.user import User
from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY, MAIL_ADDRESS

@api.route('/sign-up')
class SignUpRoute(Resource):
    def post(self):
        data = api.payload
        username = None
        password = None
        email = None
        try:
            username = data['username']
            password = data['password']
            email = data['email']

        except:
            return {"error": "Missing data."}, 400

        if len(password) < 6:
            return {"error": "Password is too short."}, 400

        if User.query.filter_by(username=username).first() != None:
            return {"error": "Username already exists"}, 400

        if User.query.filter_by(email=email).first() != None:
            return {"error": "Email already in use."}, 400

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            user = User(username=username, password=hashed_pw, email=email)
            db.session.add(user)
            db.session.commit()

            validationCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            token = jwt.encode({"id": user.id, "code": validationCode, 'exp': datetime.utcnow() + timedelta(minutes=10)}, JWT_KEY, algorithm="HS256")

            msg = Message(
                'Quoting account validation',
                sender = MAIL_ADDRESS,
                recipients = [email]
               )
            msg.body = f"Hello @{username}! Welcome to Quoting! To finish your registration, please copy the code below and paste it in the app.\n\n{validationCode}"
            mail.send(msg)
            
            data = {
                "id": user.id,
                "validation_token": token
            }

            return {"message": "User created.", "data": data}, 201
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    def put(self):
        code = api.payload['code']
        token = api.payload['token']

        if len(code) < 5:
            return {"error": "Invalid code."}, 400

        data = jwt.decode(token, JWT_KEY, algorithms="HS256")

        if data['code'] != code:
            return {"error": 'Invalid code.'}, 401

        try:
            user = User.query.filter_by(id=data['id']).first()
            user.valid = True
            db.session.add(user)
            db.session.commit()

            token = jwt.encode({"id": user.id, 'admin': user.admin, 'exp': datetime.utcnow() + timedelta(days=60)}, JWT_KEY, algorithm="HS256")
            
            data = {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "is_admin": user.admin,
                "token": token
            }

            return {"message": "Account validated.", "data": data}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

        

@api.route('/sign-in')
class SignInRoute(Resource):

    @userAuthorization
    def get(self):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']

        try:
            userData = User.query.filter_by(id=userId).first()
            if userData == None:
                return {"error": "User not found"}, 400

            user = {
                "id": userData.id,
                "username": userData.username,
                "name": userData.name,
                "is_admin": userData.admin,
            }
            return {"message": "User data retrieved", "data": user}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

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
            token = jwt.encode({"id": userData.id, 'admin': userData.admin, 'exp': datetime.utcnow() + timedelta(days=60)}, JWT_KEY, algorithm="HS256")

            if userData.active == False:
                return {"error": "This account is banned."}, 403

            if userData.valid == False:
                validationCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

                token = jwt.encode({"id": userData.id, "code": validationCode, 'exp': datetime.utcnow() + timedelta(minutes=10)}, JWT_KEY, algorithm="HS256")

                msg = Message(
                    'Quoting account validation',
                    sender = MAIL_ADDRESS,
                    recipients = [userData.email]
                )
                msg.body = f"Hello @{userData.username}! Welcome to Quoting! To finish your registration, please copy the code below and paste it in the app.\n\n{validationCode}"
                mail.send(msg)
            
                data = {
                    "id": userData.id,
                    "validation_token": token
                }

                return {"message": "Validation sent.", "data": data}, 403
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

        