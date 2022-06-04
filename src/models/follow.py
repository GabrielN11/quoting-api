from src.server.instance import db


class Follow(db.Model):
     __tablename__ = "follow"

     id = db.Column(db.Integer, primary_key=True)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     follower = db.Column(db.Integer, db.ForeignKey('user.id'))