from flask import request
from flask_restx import Resource
import jwt
from sqlalchemy import or_

from src.server.instance import api, db, bcrypt
from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share
from src.models.follow import Follow

from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY



@api.route('/admin-user/<id>')
class AdminUserRoute(Resource):

    @adminAuthorization
    def post(self, id):
        data = api.payload
        status = None
        try:
            status = data['status']
        except:
            return {"error": "Missing data."}, 400

        user = User.query.filter_by(id=id).first()
        text = 'banned' if status == False else 'active'
        if user.active == status:
            return {"error": f"User is already {text}."}, 400
        
        try:
            user.active = status
            db.session.add(user)
            db.session.commit()

            return {"message": f"User {text}."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @adminAuthorization
    def delete(self, id):
        try:
            user = User.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()

            return {"message": "User deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500   

@api.route('/admin-user-list')
class AdminUserListRoute(Resource):

    @adminAuthorization
    def get(self):
        searchQuery = request.args.get('search')
        page = 0
        limit = 20
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed."}, 400

        try:
            users = []
            if searchQuery:
                users = User.query.filter(or_(User.name.ilike("%"+searchQuery.lower()+"%"), User.username.ilike(("%"+searchQuery.lower()+"%")))).limit(limit).offset(page).all()
            else:
                users = User.query.limit(limit).offset(page).all()

            if len(users) < 1:
                return None, 204
        
            response = list(map(lambda user: {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "active": user.active,
                "is_admin": user.admin
            }, users))

            return {"message": "Users retrieved.", "data": response}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/set-admin/<id>')
class SetAdminRoute(Resource):
    
    @adminAuthorization
    def put(self, id):
        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400
        
        if user.admin:
            user.admin = False
        else:
            user.admin = True

        try:
            db.session.add(user)
            db.session.commit()

            text = f"{user.name} has admin privileges now." if user.admin else f"{user.name} is not an admin anymore."
            
            return {"message": text}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/change-password/<id>')
class AdminChangePasswordRoute(Resource):
    
    @adminAuthorization
    def put(self, id):
        data = api.payload
        password = None
        try:
            password = data['password']
        except:
            return {"error": "Missing data."}

        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        user.password = hashed_pw

        try:
            db.session.add(user)
            db.session.commit()
            
            return {"message": f"{user.name}'s password changed."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/change-name/<id>')
class AdminChangeNameRoute(Resource):
    
    @adminAuthorization
    def put(self, id):
        data = api.payload
        name = None
        try:
            name = data['name']
        except:
            return {"error": "Missing data."}

        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400

        user.name = name

        try:
            db.session.add(user)
            db.session.commit()
            
            return {"message": f"{user.username}'s name changed."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500


@api.route('/change-username/<id>')
class AdminChangeUsernameRoute(Resource):
    
    @adminAuthorization
    def put(self, id):
        data = api.payload
        username = None
        try:
            username = data['username']
        except:
            return {"error": "Missing data."}

        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400

        user.username = username

        try:
            db.session.add(user)
            db.session.commit()
            
            return {"message": "Username changed."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500