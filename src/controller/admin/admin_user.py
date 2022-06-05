from operator import or_
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

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY



@api.route('/admin-user/<id>')
class AdminUserRoute(Resource):

    @adminAuthorization
    def put(self, id):
        data = api.payload
        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400

        try:
            username = data['username']
            name = data['name']
            password = data['password']
            admin = data['is_admin']
        except:
            return {"error": "Missing data."}, 400

        user.username = username
        user.name = name
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.admin = admin

        try:
            db.session.add(user)
            db.session.commit()

            response = {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "is_admin": user.admin
            }
            return {"message": "User updated", "data": response}, 200
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
                return 204
        
            response = list(map(lambda user: {
                "name": user.name,
                "username": user.username,
                "is_admin": user.admin
            }, users))

            return {"message": "Users retrieved.", "data": response}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500


