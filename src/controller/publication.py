from flask import request
from flask_restx import Resource
from datetime import datetime, timedelta
import jwt

from sqlalchemy import desc, func

from src.server.instance import api, db
from src.utils.dateConvertion import DateConvertion

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share
from src.models.seen import Seen
from src.models.follow import Follow

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY

dateConvertion = DateConvertion()


@api.route('/publication')
@api.route('/publication/<id>')
class PublicationRoute(Resource):

    @userAuthorization
    def get(self):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']
        reset = False

        try:
            publicationCount = Publication.query.count()
            seenCount = Seen.query.filter_by(userId=userId).count()
            
            seenSubquery = db.session.query(Seen.publicationId).filter_by(userId=userId).subquery()

            publication = None

            if seenCount >= publicationCount:
                Seen.query.filter_by(userId=userId).delete()
                db.session.commit()
                reset = True
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
                "share_count": publication.share.count(),
                "reset_seen": reset
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

        lastPublication = Publication.query.filter_by(userId=userId).order_by(desc(Publication.date)).first()
        if lastPublication and (lastPublication.date + timedelta(minutes=5)) >= datetime.utcnow():
            return {"error": "Wait 5 minutes between each publication."}, 400

        publication = Publication(text=text, userId=userId, author=author)
        try:
            db.session.add(publication)
            db.session.commit()

            return {"message": "Posted.", "data": {"id": publication.id}}, 201
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def put(self, id):
        data = api.payload
        text = None
        try:
            text = data['text']
        except:
            return {"error": "Missing data."}, 400

        try:
            publication = Publication.query.filter_by(id=id).first()
            publication.text = text
            db.session.add(publication)
            db.session.commit()
            response = {
                "id": publication.id,
                "author": publication.author,
                "text": publication.text,
                "user_id": publication.userId,
                "date": str(publication.date),
                "commentaries_count": publication.commentary.count(),
                "share_count": publication.share.count(),
            }
            return {"message": "Publication updated.", "data": response}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def delete(self, id):
        try:
            publication = Publication.query.filter_by(id=id).first()
            db.session.delete(publication)
            db.session.commit()

            return {"message": "Publication deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500


@api.route('/publication-by-follow')
class PublicationByFollowRoute(Resource):

    @userAuthorization
    def get(self):
        userId = jwt.decode(request.headers.get('Authorization').split()[1], JWT_KEY, algorithms="HS256")['id']
        reset = False

        try:
            followSubquery = db.session.query(Follow.userId).filter_by(follower=userId).subquery()
            publicationCount = Publication.query.filter(Publication.userId.in_(followSubquery)).count()
            publicationSubquery = db.session.query(Publication.id).filter(Publication.userId.in_(followSubquery)).subquery()
            
            seenCount = Seen.query.filter(Seen.publicationId.in_(publicationSubquery)).filter_by(userId=userId).count()
            
            seenSubquery = db.session.query(Seen.publicationId).filter_by(userId=userId).subquery()

            publication = None

            if seenCount >= publicationCount:
                print(Seen.query.filter(Seen.publicationId.in_(publicationSubquery)).filter_by(userId=userId))
                db.engine.execute(f"""
                DELETE FROM seen WHERE publicationId IN (SELECT publication.id 
                FROM publication 
                WHERE publication.userId IN (SELECT anon_1.userId 
                FROM (SELECT follow.userId AS userId 
                FROM follow 
                WHERE follow.follower = {userId}) AS anon_1));
                """)
                db.session.commit()
                reset = True
                publication = Publication.query.filter(Publication.userId.in_(followSubquery)).order_by(func.rand()).first()
            else:
                publication = Publication.query.filter(Publication.id.not_in(seenSubquery)).filter(Publication.userId.in_(followSubquery)).order_by(func.rand()).first()

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
                "share_count": publication.share.count(),
                "reset_seen": reset
            }

            return {"message": "Publication retrieved.", "data": response}, 200
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
