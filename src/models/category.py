from src.server.instance import db
from datetime import datetime
from src.models.commentary import Commentary
from src.models.seen import Seen
from src.models.share import Share

class Category(db.Model):
     __tablename__ = "category"

     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(15), unique=True)

     publication = db.relationship('Publication', cascade="all, delete")