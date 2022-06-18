#Server instance
from src.server.instance import server

#Routes

from src.controller.authentication import SignUpRoute, SignInRoute
from src.controller.user import AlterNameRoute, AlterPasswordRoute, ProfileRoute
from src.controller.publication import PublicationsByUserRoute, PublicationRoute, PublicationByFollowRoute, PublicationByIdRoute, PinRoute
from src.controller.commentary import CommentaryRoute, CommentaryByPublicationRoute, CommentaryByUserRoute
from src.controller.share import ShareRoute, ShareByPublication
from src.controller.admin.admin_user import AdminUserRoute, AdminUserListRoute, SetAdminRoute, AdminChangePasswordRoute, AdminChangeUsernameRoute, AdminChangeNameRoute
from src.controller.admin.admin_publication import AdminPublicationRoute
from src.controller.follow import FollowRoute, FollowersRoute, FollowingRoute


if __name__ == "__main__":
    server.run()