from src.server.instance import db
from datetime import datetime

class Commentary(db.Model):
     __tablename__ = "commentary"

     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.String(500))
     date = db.Column(db.DateTime, default=datetime.utcnow)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     publicationId = db.Column(db.Integer, db.ForeignKey('publication.id'))