from src.server.instance import db


class Seen(db.Model):
     __tablename__ = "seen"

     id = db.Column(db.Integer, primary_key=True)
     publicationId = db.Column(db.Integer, db.ForeignKey('publication.id'))
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))