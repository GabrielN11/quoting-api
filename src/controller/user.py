from flask import request
from flask_restx import Resource
import jwt
from src.server.instance import api, db, bcrypt
from sqlalchemy import desc, or_

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share
from src.models.follow import Follow

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY
from src.utils.check_profanity import checkProfanity



@api.route('/profile/<id>')
class ProfileRoute(Resource):

    def get(self, id):
        try:
            user = User.query.filter_by(id=id).first()

            if user == None:
                return {"error": "Profile not found."}, 400

            publicationCount = Publication.query.filter_by(userId=user.id).count()
            commentaryCount = Commentary.query.filter_by(userId=user.id).count()
            shareCount = Share.query.filter_by(userId=user.id).count()
            pinnedPublication = Publication.query.filter_by(pinned=True).filter_by(userId=id).first()

            userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']
            follow = Follow.query.filter(Follow.follower == userId).filter(Follow.userId == id).first()

            response = {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "is_admin": user.admin,
                "active": user.active,
                "publication_count": publicationCount,
                "commentary_count": commentaryCount,
                "share_count": shareCount,
                "pinned_publication": {
                    "id": pinnedPublication.id,
                    "author": pinnedPublication.author,
                    "text": pinnedPublication.text,
                    "user_id": pinnedPublication.userId,
                    "date": str(pinnedPublication.date),
                    "pinned": pinnedPublication.pinned,
                    "commentaries_count": pinnedPublication.commentary.count(),
                    "share_count": pinnedPublication.share.count(),
                } if pinnedPublication != None else None,
                "following": follow.id if follow != None else False
            }

            return {"message": "Profile found.", "data": response}
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500    

@api.route('/alter-password/<id>')
class AlterPasswordRoute(Resource):

    @userAuthorization
    def put(self, id):
        data = api.payload
        password = None
        newPassword = None

        try:
            password = data['password']
            newPassword = data['new-password']
        except:
            return {"error": "Missing data."}, 400

        if len(newPassword) < 6:
            return {"error": "New password is too short."}, 400

        user = User.query.filter_by(id=id).first()
        if user == None:
            return {"error": "User not found."}, 400

        if bcrypt.check_password_hash(user.password, password=password):
            hashed_pw = bcrypt.generate_password_hash(newPassword).decode('utf-8')
            user.password = hashed_pw

            try:
                db.session.add(user)
                db.session.commit()
                return {"message": "Password updated."}, 200
            except Exception as err:
                print(str(err))
                return {"error": "Error connecting to database. Try again later."}, 500
        else:
            return {"error": "Invalid password."}, 400

@api.route('/alter-name/<id>')
class AlterNameRoute(Resource):
    @userAuthorization
    def put(self, id):
        data = api.payload
        name = None

        try:
            name = data['name']
        except:
            return {"error": "Missing data."}, 400

        if checkProfanity([name]):
            return {"error": "Invalid display name."}, 400

        try:
            user = User.query.filter_by(id=id).first()
            
            if(user == None):
                return {"error": "User do not exists."}, 400

            user.name = name

            db.session.add(user)
            db.session.commit()

            return {"message": "Name updated."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/user-list')
class UserListRoute(Resource):

    @userAuthorization
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