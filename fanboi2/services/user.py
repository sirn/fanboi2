import datetime
import secrets

from passlib.context import CryptContext
from sqlalchemy.sql import and_, or_, func

from ..auth import SESSION_TOKEN_VALIDITY
from ..models import User, UserSession


ARGON2_MEMORY_COST = 1024
ARGON2_PARALLELISM = 2
ARGON2_ROUNDS = 6


def _create_crypt_context():
    return CryptContext(
        schemes=['argon2'],
        deprecated=['auto'],
        truncate_error=True,
        argon2__memory_cost=ARGON2_MEMORY_COST,
        argon2__parallelism=ARGON2_PARALLELISM,
        argon2__rounds=ARGON2_ROUNDS)


class UserCreateService(object):
    """User create service provides a service for creating user."""

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.crypt_context = _create_crypt_context()

    def create(self, username, password, parent_id, groups=[]):
        """Creates a user. :param:`parent_id` must be present for all users
        except the root user, usually the user who created this specific user.

        :param username: A username.
        :param password: A password.
        :parent parent_id: An :type:`int` ID of the user who created this user.
        """
        user = User(
            username=username,
            encrypted_password=self.crypt_context.hash(password),
            parent_id=parent_id)

        self.dbsession.add(user)
        self.dbsession.flush()
        return user


class UserLoginService(object):
    """User login service provides a service for managing user logins."""

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.crypt_context = _create_crypt_context()

    def _generate_token(self):
        """Generates a secure random token."""
        return secrets.token_urlsafe(48)

    def authenticate(self, username, password):
        """Returns :type:`True` if the given username and password combination
        could be authenticated or :type:`False` otherwise.

        :param username: A username :type:`str` to authenticate.
        :param password: A password :type:`str` to authenticate.
        """
        user = self.dbsession.query(User).\
            filter(and_(User.deactivated == False,  # noqa: E711
                        User.username == username)).\
            first()
        if not user:
            return False

        ok, new_hash = self.crypt_context.verify_and_update(
            password,
            user.encrypted_password)
        if not ok:
            return False

        if new_hash is not None:
            user.encrypted_password = new_hash
            self.dbsession.add(user)
            self.dbsession.flush()
        return True

    def _user_session_q(self, token, ip_address):
        """Internal method for querying user from token."""
        return self.dbsession.query(User).\
            join(User.sessions).\
            filter(and_(User.deactivated == False,  # noqa: E711
                        UserSession.token == token,
                        UserSession.ip_address == ip_address,
                        or_(UserSession.revoked_at == None,  # noqa: E711
                            UserSession.revoked_at >= func.now())))

    def user_from_token(self, token, ip_address):
        """Returns a :class:`User` by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        return self._user_session_q(token, ip_address).first()

    def groups_from_token(self, token, ip_address):
        """Return list of group names by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        """
        user = self._user_session_q(token, ip_address).first()
        if user is None:
            return None
        return [g.name for g in user.groups]

    def revoke_token(self, token):
        """Revoke the given token. This method should be called when the user
        is logging out.

        :param token: A user login token :type:`str`.
        """
        user_session = self.dbsession.query(UserSession).\
            filter(and_(UserSession.token == token,
                        or_(UserSession.revoked_at == None,  # noqa: E711
                            UserSession.revoked_at >= func.now()))).\
            first()
        if user_session is None:
            return None
        user_session.revoked_at = func.now()
        self.dbsession.add(user_session)
        self.dbsession.flush()
        return user_session

    def mark_seen(self, token, ip_address, revocation=SESSION_TOKEN_VALIDITY):
        """Mark the given token as seen and extend the token validity period
        by the given :param:`revocation` seconds.

        :param token: A user login token :type:`str`.
        :param ip_address: IP address of the user.
        :param revocation: Number of seconds until the token is invalidated.
        """
        last_seen_at = datetime.datetime.now()
        revoked_at = last_seen_at + datetime.timedelta(seconds=revocation)
        user_session = self.dbsession.query(UserSession).\
            join(UserSession.user).\
            filter(and_(User.deactivated == False,  # noqa: E711
                        UserSession.token == token,
                        UserSession.ip_address == ip_address,
                        or_(UserSession.revoked_at == None,  # noqa: E711
                            UserSession.revoked_at >= func.now()))).\
            first()
        if user_session is None:
            return None
        user_session.last_seen_at = func.now()
        user_session.revoked_at = revoked_at
        self.dbsession.add(user_session)
        self.dbsession.flush()
        return user_session

    def token_for(self, username, ip_address):
        """Create a new token for the given :param:`username`.

        :param username: A username to create token for.
        :param ip_address: IP address that used to retrieve this token.
        """
        user = self.dbsession.query(User).\
            filter(and_(User.deactivated == False,  # noqa: E711
                        User.username == username)).\
            one()

        user_session = UserSession(
            user=user,
            ip_address=ip_address,
            token=self._generate_token())

        self.dbsession.add(user_session)
        self.dbsession.flush()
        return user_session.token
