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



@api.route('/admin-publication/<id>')
class AdminPublicationRoute(Resource):

    @adminAuthorization
    def put(self, id):
        data = api.payload
        text = None
        author = None

        try:
            text = data['text']
            author = data['author']
        except:
            return {"error": "Missing data."}, 400

        try:
            publication = Publication.query.filter_by(id=id).first()
            if publication == None:
                return {"error": "Missing data."}, 400
            publication.text = text
            publication.author = author

            db.session.add(publication)
            db.session.commit()

            return {"message": "Publication updated."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @adminAuthorization
    def delete(self, id):
        try:
            publication = Publication.query.filter_by(id=id).first()
            if publication == None:
                return {"error": "Publication not found."}, 400
                
            db.session.delete(publication)
            db.session.commit()

            return {"message": "Publication deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500   


