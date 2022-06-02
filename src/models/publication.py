from src.server.instance import db
from sqlalchemy import func

from src.models.commentary import Commentary
from src.models.seen import Seen

class Publication(db.Model):
     __tablename__ = "publication"

     id = db.Column(db.Integer, primary_key=True)
     text = db.Column(db.String(1000))
     author = db.Column(db.String(20), nullable=True)
     password = db.Column(db.String(100))
     date = db.Column(db.DateTime, server_default=func.now())
     pinned = db.Column(db.BOOLEAN, default=False)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))

     commentary = db.relationship('Commentary', cascade="all, delete")
     seen = db.relationship('Seen', cascade="all, delete")