from flask import request
from flask_restx import Resource
import jwt
from src.server.instance import api, db

from src.models.category import Category

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization
from env import JWT_KEY

@api.route('/category')
@api.route('/category/<id>')
class CategoryRoute(Resource):

    @userAuthorization
    def get(self):
        try:
            categories = Category.query.all()
            response = list(map(lambda category: {
                "id": category.id,
                "name": category.name
            }, categories))
            return {"message": "Categories retrieved.", "data": response}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    def post(self):
        name = api.payload['name']
        if not name:
            return {"error": "Missing data."}, 400
        if len(name) > 15 or len(name) < 3:
            return {"error": "Invalid name length"}, 400
        
        try:
            categoryExists = Category.query.filter_by(name=name).first()
            if categoryExists:
                return {"error": "Category name already exists."}, 400
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500
        
        try:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()

            return {"message": "Category created."}, 201
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500 
    
    @adminAuthorization
    def put(self, id):
        name = api.payload['name']
        if not name:
            return {"error": "Missing data."}, 400
        if len(name) > 15 or len(name) < 3:
            return {"error": "Invalid name length"}, 400

        try:
            categoryExists = Category.query.filter_by(name=name).first()
            if categoryExists:
                return {"error": "Category name already exists."}, 400
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500
        
        try:
            category = Category.query.filter_by(id=id).first()
            category.name = name
            db.session.add(category)
            db.session.commit()

            return {"message": "Category altered."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @adminAuthorization
    def delete(self, id):    
        try:
            category = Category.query.filter_by(id=id).first()
            db.session.delete(category)
            db.session.commit()

            return {"message": "Category deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500