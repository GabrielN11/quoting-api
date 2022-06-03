from flask import request
from flask_restx import Resource
from datetime import datetime, timedelta
import jwt
from random import randint

from sqlalchemy import desc, func

from src.server.instance import api, db, bcrypt

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share
from src.models.seen import Seen

from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY


@api.route('/publication')
class PublicationRoute(Resource):

    @userAuthorization
    def get(self):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']

        try:
            publicationCount = Publication.query.count()
            seenCount = Seen.query.filter_by(userId=userId).count()
            
            seenSubquery = db.session.query(Seen.publicationId).filter_by(userId=userId).subquery()

            publication = None

            if seenCount >= publicationCount:
                Seen.query.filter_by(userId=userId).delete()
                db.session.commit()
                publication = Publication.query.order_by(func.rand()).first()
            else:
                publication = Publication.query.filter(Publication.id.not_in(seenSubquery)).order_by(func.rand()).first()

            seen = Seen(publicationId=publication.id, userId=userId)
            db.session.add(seen)
            db.session.commit()

            response = {
                "id": publication.id,
                "author": publication.author,
                "text": publication.text,
                "user_id": publication.userId,
                "date": str(publication.date),
                "commentaries_count": publication.commentary.count(),
                "share_count": publication.share.count()
            }

            return {"message": "Publication retrieved.", "data": response}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500




    
    @userAuthorization
    def post(self):
        data = api.payload
        text = None
        author = None
        userId = None

        try:
            text = data['text']
            userId = data['user_id']
            author = data['author']
        except:
            return {"error": "Missing data."}, 400

        publication = Publication(text=text, userId=userId, author=author)

        try:
            db.session.add(publication)
            db.session.commit()

            return {"message": "Posted.", "data": {"id": publication.id}}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/publications-by-user/<id>')
class PublicationsByUserRoute(Resource):
    def get(self, id):
        limit = 10
        page = 0

        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400


        try:
            publications = Publication.query.filter(Publication.userId == id).order_by(desc(Publication.date)).limit(limit).offset(page).all()
            
            if len(publications) == 0:
                return 204
            
            responseArray = list(map(lambda publication: {
                "id": publication.id,
                "author": publication.author,
                "text": publication.text,
                "user_id": publication.userId,
                "date": str(publication.date),
                "commentaries_count": publication.commentary.count(),
                "share_count": publication.share.count()
            }, publications))

            return {"message": "Publications retrieved.", "data": responseArray}, 200

        except Exception as err:
            print(str(err))
            return {"error": 'Error connecting to database. Try again later.'}, 500
