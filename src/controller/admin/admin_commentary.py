from flask_restx import Resource

from src.server.instance import api, db
from src.models.commentary import Commentary


from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY



@api.route('/admin-commentary/<id>')
class AdminCommentaryRoute(Resource):

    @adminAuthorization
    def put(self, id):
        data = api.payload
        text = None

        try:
            text = data['text']
        except:
            return {"error": "Missing data."}, 400

        try:
            commentary = Commentary.query.filter_by(id=id).first()
            if commentary == None:
                return {"error": "Missing data."}, 400
            commentary.text = text

            db.session.add(commentary)
            db.session.commit()

            return {"message": "commentary updated."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @adminAuthorization
    def delete(self, id):
        try:
            commentary = Commentary.query.filter_by(id=id).first()
            if commentary == None:
                return {"error": "commentary not found."}, 400
                
            db.session.delete(commentary)
            db.session.commit()

            return {"message": "commentary deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500   


