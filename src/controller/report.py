from flask import request
from flask_restx import Resource
from src.server.instance import api, db
from sqlalchemy import desc
from datetime import datetime, timedelta

from src.models.report import Report
from src.models.user import User
from src.models.commentary import Commentary
from src.models.publication import Publication

from src.authorization.user_authorization import userAuthorization
from src.authorization.admin_authorization import adminAuthorization

@api.route('/report')
@api.route('/report/<id>')
class ReportRoute(Resource):

    @adminAuthorization
    def get(self, id):
        try:
            report = Report.query.filter_by(id=id).first()
            if report == None:
                return {"error": "Report not found"}, 400

            user = User.query.filter_by(id=report.userId).first()
            commentaryDic = None
            publicationDic = None

            if report.publicationId:
                publication = Publication.query.filter_by(id=report.publicationId).first()
                if publication == None:
                    pass
                else:
                    publicationDic = {
                    "id": publication.id,
                    "author": publication.author,
                    "text": publication.text,
                    "user_id": publication.userId,
                    "date": str(publication.date),
                    "commentaries_count": publication.commentary.count(),
                    "share_count": publication.share.count(),
                }
            else:
                commentary = Commentary.query.filter_by(id=report.commentaryId).first()
                if commentary == None:
                    pass
                else:
                    commentaryDic = {
                    "id": commentary.id,
                    "text": commentary.text,
                    "user_id": commentary.userId,
                    "publication_id": commentary.publicationId,
                    "share_count": commentary.share.count(),
                    "date": str(commentary.date),
                }
            
            response = {
                "id": report.id,
                "title": report.title,
                "text": report.text,
                "date": str(report.date),
                "closed": report.closed,
                "publication_id": report.publicationId,
                "commentary_id": report.commentaryId,
                "user": {
                    "id": user.id,
                    "username": user.username
                },
                "publication": publicationDic,
                "commentary": commentaryDic
            }

            return {"message": "Report retrieved", "data": response}, 200
            
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @userAuthorization
    def post(self):
        data = api.payload
        title = None
        text = None
        userId = None
        publicationId = None
        commentaryId = None
        try:
            title = data['title']
            text = data['text']
            userId = data['user_id']
            publicationId = data['publication_id']
            commentaryId = data['commentary_id']
        except:
            return {"error": "Missing data."}, 400

        if len(title) > 40 or len(text) > 500 or len(title) < 3 or len(text) < 20:
            return {"error": "Invalid text or title."}, 400

        lastReport = Report.query.filter_by(userId=userId).order_by(desc(Report.date)).first()
        if lastReport and (lastReport.date + timedelta(minutes=2)) >= datetime.utcnow():
            return {"error": "Wait 2 minutes between each report."}, 400

        try:
            report = Report(title=title, text=text, publicationId=publicationId, commentaryId=commentaryId, userId=userId)
            db.session.add(report)
            db.session.commit()
            
            return {"message": "Report sent."}, 201
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500 
    
    @adminAuthorization
    def put(self, id):
        try:
            report = Report.query.filter_by(id=id).first()
            if report == None:
                return {"error": "Report not found."}, 400
            
            report.closed = not report.closed

            db.session.add(report)
            db.session.commit()
            
            message = "Report closed." if report.closed == False else "Report opened."
            return {"message": message, "data": report.closed}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

    @adminAuthorization
    def delete(self, id):    
        try:
            report = Report.query.filter_by(id=id).first()
            db.session.delete(report)
            db.session.commit()

            return {"message": "Report deleted."}, 200
        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/report-list')
class ReportListRoute(Resource):

    @adminAuthorization
    def get(self):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400

        try:
            reports = Report.query.filter_by(closed=False).order_by(desc(Report.date)).limit(limit).offset(page).all()
            if len(reports) == 0:
                return None, 204

            def getUserReport(report):
                user = User.query.filter_by(id=report.userId).first()
                return {
                    "id": report.id,
                    "title": report.title,
                    "date": str(report.date),
                    "user": {
                        "id": user.id,
                        "username": user.username
                    }
                }

            responseArray = list(map(getUserReport, reports))

            return {"message": "Reports retrieved", "data": responseArray}, 200

        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500

@api.route('/report-closed-list')
class ReportClosedListRoute(Resource):

    @adminAuthorization
    def get(self):
        limit = 10
        page = 0
        try:
            page = int(request.args.get('page')) * 10
        except:
            return {"error": "Page not informed correctly."}, 400

        try:
            reports = Report.query.filter_by(closed=True).order_by(desc(Report.date)).limit(limit).offset(page).all()

            if len(reports) == 0:
                return None, 204


            def getUserReport(report):
                user = User.query.filter_by(id=report.userId).first()
                return {
                    "id": report.id,
                    "title": report.title,
                    "date": str(report.date),
                    "user": {
                        "id": user.id,
                        "username": user.username
                    }
                }

            responseArray = list(map(getUserReport, reports))

            return {"message": "Closed reports retrieved", "data": responseArray}, 200

        except Exception as err:
            print(str(err))
            return {"error": "Error connecting to database. Try again later."}, 500