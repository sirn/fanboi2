import datetime
import secrets

from passlib.context import CryptContext
from sqlalchemy.sql import and_, or_, func, desc
from sqlalchemy.orm import joinedload

from ..auth import SESSION_TOKEN_VALIDITY
from ..models import User, UserSession, Group


ARGON2_MEMORY_COST = 1024
ARGON2_PARALLELISM = 2
ARGON2_ROUNDS = 6


def _create_crypt_context():
    return CryptContext(
        schemes=["argon2"],
        deprecated=["auto"],
        truncate_error=True,
        argon2__memory_cost=ARGON2_MEMORY_COST,
        argon2__parallelism=ARGON2_PARALLELISM,
        argon2__rounds=ARGON2_ROUNDS,
    )


class UserCreateService(object):
    """User create service provides a service for creating user."""

    def __init__(self, dbsession, identity_svc):
        self.dbsession = dbsession
        self.identity_svc = identity_svc
        self.crypt_context = _create_crypt_context()

    def create(self, parent_id, username, password, name, groups=None):
        """Creates a user. :param:`parent_id` must be present for all users
        except the root user, usually the user who created this specific user.

        :param parent_id: An :type:`int` ID of the user who created this user.
        :param username: A username.
        :param password: A password.
        :param name: A default name to use when posted in board.
        :param groups: Group the user belongs to.
        """
        if not groups:
            groups = []

        ident_type = "ident"
        if "admin" in groups:
            ident_type = "ident_admin"

        user = User(
            username=username,
            name=name,
            ident_type=ident_type,
            ident=self.identity_svc.identity_for(username=username),
            encrypted_password=self.crypt_context.hash(password),
            parent_id=parent_id,
        )

        for g in groups:
            group = self.dbsession.query(Group).filter_by(name=g).first()
            if not group:
                group = Group(name=g)
            user.groups.append(group)

        self.dbsession.add(user)
        return user


class UserLoginService(object):
    """User login service provides a service for managing user logins."""

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.crypt_context = _create_crypt_context()
        self.sessions_map = {}

    def _generate_token(self):
        """Generates a secure random token."""
        return secrets.token_urlsafe(48)

    def authenticate(self, username, password):
        """Returns :type:`True` if the given username and password combination
        could be authenticated or :type:`False` otherwise.

        :param username: A username :type:`str` to authenticate.
        :param password: A password :type:`str` to authenticate.
        """
        user = (
            self.dbsession.query(User)
            .filter(
                and_(User.deactivated == False, User.username == username)  # noqa: E711
            )
            .first()
        )
        if not user:
            return False

        ok, new_hash = self.crypt_context.verify_and_update(
            password, user.encrypted_password
        )
        if not ok:
            return False

        if new_hash is not None:
            user.encrypted_password = new_hash
            self.dbsession.add(user)
        return True

    def _user_session_c(self, token, ip_address):
        """Internal method for querying user session object and cache
        it throughout the request lifecycle.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        if not (token, ip_address) in self.sessions_map:
            user_session = (
                self.dbsession.query(UserSession)
                .options(joinedload(UserSession.user))
                .filter(
                    and_(
                        UserSession.token == token,
                        UserSession.ip_address == ip_address,
                        UserSession.last_seen_at != None,  # noqa: E711
                        or_(
                            UserSession.revoked_at == None,  # noqa: E711
                            UserSession.revoked_at >= func.now(),
                        ),
                    )
                )
                .first()
            )
            self.sessions_map[(token, ip_address)] = user_session
        return self.sessions_map[(token, ip_address)]

    def _user_c(self, token, ip_address):
        """Internal method for querying user object from a session
        and cache it throughout the request lifecycle.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        user_session = self._user_session_c(token, ip_address)
        if user_session is None:
            return None
        user = user_session.user
        if user.deactivated:
            return None
        return user

    def user_from_token(self, token, ip_address):
        """Returns a :class:`User` by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        return self._user_c(token, ip_address)

    def groups_from_token(self, token, ip_address):
        """Return list of group names by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        user = self._user_c(token, ip_address)
        if user is None:
            return None
        return [g.name for g in user.groups]

    def revoke_token(self, token, ip_address):
        """Revoke the given token. This method should be called when the user
        is logging out.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        user_session = self._user_session_c(token, ip_address)
        if user_session is None:
            return None
        user_session.revoked_at = func.now()
        self.dbsession.add(user_session)
        return user_session

    def mark_seen(self, token, ip_address, revocation=SESSION_TOKEN_VALIDITY):
        """Mark the given token as seen and extend the token validity period
        by the given :param:`revocation` seconds.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        :param revocation: Number of seconds until the token is invalidated.
        """
        user_session = self._user_session_c(token, ip_address)
        if user_session is None:
            return None
        if user_session.user.deactivated:
            return None
        user_session.last_seen_at = func.now()
        user_session.revoked_at = func.now() + datetime.timedelta(seconds=revocation)
        self.dbsession.add(user_session)
        return user_session

    def token_for(self, username, ip_address):
        """Create a new token for the given :param:`username`.

        :param username: A username to create token for.
        :param ip_address: IP address that used to retrieve this token.
        """
        user = (
            self.dbsession.query(User)
            .filter(
                and_(User.deactivated == False, User.username == username)  # noqa: E711
            )
            .one()
        )

        user_session = UserSession(
            user=user,
            ip_address=ip_address,
            token=self._generate_token(),
            last_seen_at=func.now(),
        )

        self.dbsession.add(user_session)
        return user_session.token


class UserQueryService(object):
    """User query service provides a service for querying users."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def user_from_id(self, id):
        """Returns a user matching ID. Raises :class:`NoResultFound` is
        user could not be found.

        :param id: A user `type`:int: id.
        """
        return self.dbsession.query(User).filter_by(id=id).one()


class UserSessionQueryService(object):
    """User session query service provides a service for querying
    user sessions.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_recent_from_user_id(self, user_id):
        """Query recent sessions for the given user ID.

        :param user_id: A user `type`:int: id.
        """
        return list(
            self.dbsession.query(UserSession)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.last_seen_at != None,  # noqa: E711
                )
            )
            .order_by(desc(UserSession.last_seen_at))
            .limit(5)
            .all()
        )
