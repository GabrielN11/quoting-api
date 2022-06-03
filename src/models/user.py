from src.server.instance import db
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.seen import Seen
from src.models.share import Share

class User(db.Model):
     __tablename__ = "user"

     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), unique=True)
     name = db.Column(db.String(25), default='Anonymous')
     password = db.Column(db.String(100))
     admin = db.Column(db.BOOLEAN, default=False)
     
     publication = db.relationship('Publication', cascade="all, delete")
     seen = db.relationship('Seen', cascade="all, delete", lazy='dynamic')
     commentary = db.relationship('Commentary', cascade="all, delete")
     share = db.relationship('Share', cascade="all, delete")