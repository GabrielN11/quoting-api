from flask import request
from flask_restx import Resource
from sqlalchemy import desc

from src.server.instance import api, db

from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.share import Share

from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY


@api.route('/commentary')
@api.route('/commentary/<id>')
class CommentaryRoute(Resource):
    
    @userAuthorization
    def post(self):
        data = api.payload
        text = None
        userId = None
        publicationId = None

        try:
            text = data['text']
            userId = data['user_id']
            publicationId = data['publication_id']
        except:
            return {"error": "Missing data."}, 400

        if Publication.query.filter_by(id=publicationId).count() < 1 and User.query.filter_by(id=userId).count() < 1:
            return {"error": "Invalid publication or user."}, 400
        
        commentary = Commentary(userId=userId, publicationId=publicationId, text=text)

        try:
            db.session.add(commentary)
            db.session.commit()

            response = {
                "id": commentary.id,
                "date": str(commentary.date),
                "text": commentary.text,
                "user_id": commentary.userId,
                "publication_id": commentary.publicationId
            }

            return {"message": "Commentary published.", "data": response}, 201

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
            commentary = Commentary.query.filter_by(id=id).first()
            commentary.text = text
            db.session.add(commentary)
            db.session.commit()

            response = {
                "id": commentary.id,
                "text": commentary.text,
                "user_id": commentary.userId,
                "publication_Id": commentary.publicationId,
                "date": str(commentary.date)
            }

            return {"message": "Commentary updated.", "data": response}, 200
            
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def delete(self, id):
        try:
            commentary = Commentary.query.filter_by(id=id).first()
            db.session.delete(commentary)
            db.session.commit()

            return {"message": "Commentary deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500
        
@api.route('/commentary-by-publication/<id>')
class CommentaryByPublicationRoute(Resource):

    def get(self, id):
        limit = 10
        page = 0

        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400


        try:
            commentaries = Commentary.query.filter(Commentary.publicationId == id).order_by(desc(Commentary.date)).limit(limit).offset(page).all()
            
            if len(commentaries) == 0:
                return 204
            
            responseArray = list(map(lambda commentary: {
                "id": commentary.id,
                "text": commentary.text,
                "user_id": commentary.userId,
                "publication_id": commentary.publicationId,
                "date": str(commentary.date),
            }, commentaries))

            return {"message": "Commentaries retrieved.", "data": responseArray}, 200

        except Exception as err:
            print(str(err))
            return {"error": 'Error connecting to database. Try again later.'}, 500


@api.route('/commentary-by-user/<id>')
class CommentaryByUserRoute(Resource):

    def get(self, id):
        limit = 10
        page = 0

        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400


        try:
            commentaries = Commentary.query.filter(Commentary.userId == id).order_by(desc(Commentary.date)).limit(limit).offset(page).all()
            
            if len(commentaries) == 0:
                return 204
            
            responseArray = list(map(lambda commentary: {
                "id": commentary.id,
                "text": commentary.text,
                "user_id": commentary.userId,
                "publication_id": commentary.publicationId,
                "date": str(commentary.date),
            }, commentaries))

            return {"message": "Commentaries retrieved.", "data": responseArray}, 200

        except Exception as err:
            print(str(err))
            return {"error": 'Error connecting to database. Try again later.'}, 500



