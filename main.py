#Server instance
from src.server.instance import server

#Routes

from src.controller.authentication import SignUpRoute, SignInRoute
from src.controller.user import AlterNameRoute, AlterPasswordRoute, ProfileRoute
from src.controller.publication import PublicationsByUserRoute, PublicationRoute
from src.controller.commentary import CommentaryRoute, CommentaryByPublicationRoute, CommentaryByUserRoute


if __name__ == "__main__":
    server.run()