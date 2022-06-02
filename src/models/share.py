from src.server.instance import db

class Share(db.Model):
     __tablename__ = "share"

     id = db.Column(db.Integer, primary_key=True)
     userId = db.Column(db.Integer, db.ForeignKey('user.id'))
     publicationId = db.Column(db.Integer, db.ForeignKey('publication.id'), nullable=True)
     commentaryId = db.Column(db.Integer, db.ForeignKey('commentary.id'), nullable=True)