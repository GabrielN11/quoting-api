from src.server.instance import db
from datetime import datetime
from src.models.commentary import Commentary
from src.models.seen import Seen
from src.models.share import Share

class Publication(db.Model):
     __tablename__ = "publication"

     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.String(1000))
     author = db.Column(db.String(20), nullable=True)
     date = db.Column(db.DateTime, default=datetime.utcnow)
     pinned = db.Column(db.BOOLEAN, default=False)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))

     commentary = db.relationship('Commentary', cascade="all, delete", lazy='dynamic')
     share = db.relationship("Share", cascade="all, delete", lazy='dynamic')
     seen = db.relationship('Seen', cascade="all, delete")