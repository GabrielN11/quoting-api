from flask import request
from flask_restx import Resource
from datetime import datetime, timedelta
from sqlalchemy import desc

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

        try:
            shares = Share.query.filter_by(userId=id).limit(limit).offset(page).all()

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

            return {"message": "Content shared in your profile."}, 200
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