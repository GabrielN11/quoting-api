from sqlalchemy import func
from src.server.instance import db

class Commentary(db.Model):
     __tablename__ = "commentary"

     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.String(500))
     author = db.Column(db.String(25), nullable=True)
     date = db.Column(db.DateTime, server_default=func.now())
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     publicationId = db.Column(db.Integer, db.ForeignKey('publication.id'))