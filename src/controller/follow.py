from flask import request
from flask_restx import Resource
import jwt
from src.server.instance import api, db, bcrypt

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share
from src.models.follow import Follow

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY

@api.route('/follow/<id>')
class FollowRoute(Resource):

    @userAuthorization
    def get(self, id):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']
        try:
            follow = Follow.query.filter(Follow.follower == userId).filter(Follow.userId == id).first()
            if follow == None:
                return {"message": "Not Following"}, 204
            else:
                return {"message": "Following", "data": follow.id}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def post(self, id):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']

        if userId == int(id):
            return {"error": "User can't follow himself."}, 400
        try:
            follow = Follow(follower=userId, userId=id)
            db.session.add(follow)
            db.session.commit()

            return {"message": "User followed.", "data": follow.id}, 201
        except Exception as err:
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def delete(self, id):
        try:
            follow = Follow.query.filter_by(id=id).first()
            db.session.delete(follow)
            db.session.commit()
            return {"message": "User unfollowed."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/following/<id>')
class FollowingRoute(Resource):

    def get(self, id):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400
        
        try:
            followSubquery = db.session.query(Follow.userId).filter_by(follower=id).subquery()
            users = User.query.filter(User.id.in_(followSubquery)).filter_by(active=True).limit(limit).offset(page).all()

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

@api.route('/followers/<id>')
class FollowersRoute(Resource):

    def get(self, id):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400
        
        try:
            followSubquery = db.session.query(Follow.follower).filter_by(userId=id).subquery()
            users = User.query.filter(User.id.in_(followSubquery)).filter_by(active=True).limit(limit).offset(page).all()

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
        