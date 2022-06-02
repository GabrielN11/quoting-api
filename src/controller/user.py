from flask_restx import Resource
from datetime import datetime, timedelta

from src.server.instance import api, db
from src.models.user import User
from src.authorization.user_authorization import userAuthorization
from env import JWT_KEY

@api.route('/update-name/<id>')
class AlterNameRoute(Resource):
    @userAuthorization
    def put(self, id):
        data = api.payload
        name = None

        try:
            name = data['name']
        except:
            return {"error": "Missing data."}, 400

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
        