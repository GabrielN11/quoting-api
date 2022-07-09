from src.server.instance import db
from datetime import datetime

class Report(db.Model):
     __tablename__ = "report"

     id = db.Column(db.Integer, primary_key=True)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     title = db.Column(db.String(40))
     text = db.Column(db.String(500))
     date = db.Column(db.DateTime, default=datetime.utcnow)
     closed = db.Column(db.BOOLEAN, default=False)
     publicationId = db.Column(db.Integer, nullable=True)
     commentaryId = db.Column(db.Integer, nullable=True)