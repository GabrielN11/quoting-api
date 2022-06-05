from src.server.instance import db
from datetime import datetime

from src.models.share import Share

class Commentary(db.Model):
     __tablename__ = "commentary"

     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.String(500))
     date = db.Column(db.DateTime, default=datetime.utcnow)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     publicationId = db.Column(db.Integer, db.ForeignKey('publication.id'))

     share = db.relationship("Share", cascade="all, delete", lazy='dynamic')