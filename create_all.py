from src.models.user import User
from src.models.publication import Publication
from src.models.commentary import Commentary
from src.models.seen import Seen
from src.models.share import Share
from src.models.follow import Follow
from src.models.category import Category

from src.server.instance import db

db.create_all()