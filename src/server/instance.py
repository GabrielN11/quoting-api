from flask_restx import Api
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from env import MYSQL_PASSWORD, MYSQL_DBNAME, MYSQL_HOST, MYSQL_USER

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        cors = CORS(self.app, resources={r'*': {'origins': '*'}})
        CORS(self.app)
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DBNAME}'
        self.db = SQLAlchemy(self.app)
        self.bcrypt = Bcrypt(self.app)
        self.api = Api(self.app, 
            version='1.0',
            title='Quoting API',
            description="Quoting App's Restful API.",
            doc='/docs'
        )

    def run(self):
        self.app.run(debug=True)


server = Server()
api = server.api
db = server.db
bcrypt = server.bcrypt