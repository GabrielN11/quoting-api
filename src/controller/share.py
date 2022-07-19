from flask import request
from flask_restx import Resource
import jwt
from sqlalchemy import desc, or_

from src.server.instance import api, db, bcrypt

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share

from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY


@api.route('/share/<id>')
@api.route('/share')
class ShareRoute(Resource):

    def get(self, id):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400

        user = User.query.filter_by(id=id).first()
        if user.active == False:
            return {"error": "This user is banned."}, 403

        try:
            shares = Share.query.filter_by(userId=id).order_by(desc(Share.date)).limit(limit).offset(page).all()

            if len(shares) == 0:
                return None, 204

            def getContent(share):
                if share.publicationId:
                    publication = Publication.query.filter_by(id=share.publicationId).first()
                    response = {
                        "id": publication.id,
                        "author": publication.author,
                        "text": publication.text,
                        "user_id": publication.userId,
                        "date": str(publication.date),
                        "commentaries_count": publication.commentary.count(),
                        "share_count": publication.share.count(),
                        "user": {
                            "id": user.id,
                            "name": user.name
                        },
                        "type": "publication"
                    }
                    return response
                else:
                    commentary = Commentary.query.filter_by(id=share.commentaryId).first()
                    response = {
                        "id": commentary.id,
                        "date": str(commentary.date),
                        "text": commentary.text,
                        "user_id": commentary.userId,
                        "publication_id": commentary.publicationId,
                        "share_count": commentary.share.count(),
                        "user": {
                            "id": user.id,
                            "name": user.name
                        },
                        "type": "commentary"
                    }
                    return response

            content = list(map(getContent, shares))

            return {"message": "Shares retrieved.", "data": content}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500
    
    @userAuthorization
    def post(self):
        data = api.payload
        userId = None
        publicationId = None
        commentaryId = None
        try:
            userId = data['user_id']
            publicationId = data['publication_id']
            commentaryId = data['commentary_id']
        except:
            return {"error": "Missing data."}, 400

        if publicationId:
            publication = Publication.query.filter_by(id=publicationId).first()
            if publication.userId == userId:
                return {"error": "Can't share your own publication."}, 400
        else:
            commentary = Commentary.query.filter_by(id=commentaryId).first()
            if commentary.userId == userId:
                return {"error": "Can't share your own commentary."}, 400

        try:
            share = Share(userId=userId, publicationId=publicationId, commentaryId=commentaryId)
            db.session.add(share)
            db.session.commit()

            return {"message": "Content shared in your profile.", "data": share.id}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    def delete(self, id):
        share = Share.query.filter_by(id=id).first()
        if share == None:
            return {"error": "Shared content not found."}, 400

        try:
            db.session.delete(share)
            db.session.commit()
            return {"message": "Share removed."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/share-by-publication/<id>/<type>')
class ShareByPublication(Resource):

    @userAuthorization
    def get(self, id, type):
        userId = userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']
        if type == 'publication':
            share = Share.query.filter(Share.userId == userId).filter_by(publicationId=id).first()
            if share == None:
                return 204
            return {"data": share.id}, 200
        else:
            share = Share.query.filter(Share.userId == userId).filter_by(commentaryId=id).first()
            if share == None:
                return 204
            return {"data": share.id}, 200

@api.route('/users-by-share/<id>')
class UsersByShare(Resource):

    def get(self, id):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400
        
        try:
            shareSubquery = db.session.query(Share.userId).filter(or_(Share.publicationId == id, Share.commentaryId == id)).subquery()
            users = User.query.filter(User.id.in_(shareSubquery)).filter_by(active=True).limit(limit).offset(page).all()

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
