import secrets

from passlib.context import CryptContext
from sqlalchemy.sql import and_, or_, func

from ..models import User, UserSession


class UserLoginService(object):
    """User login service provides a service for managing user logins."""

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.crypt_context = CryptContext(
            schemes=['argon2'],
            deprecated=['auto'],
            truncate_error=True,
            argon2__memory_cost=1024,
            argon2__parallelism=2,
            argon2__rounds=6)

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
            filter_by(username=username).\
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

    def user_from_token(self, token):
        """Returns a :class:`User` by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        """
        return self.dbsession.query(User).\
            join(User.sessions).\
            filter(and_(or_(UserSession.revoked_at == None,  # noqa: E711
                            UserSession.revoked_at >= func.now()),
                        UserSession.token == token)).\
            first()

    def groups_from_token(self, token):
        """Return list of group names by looking up the given :param:`token`
        or :type:`None` if the token does not exists or has been revoked.

        :param token: A user login token :type:`str`.
        """
        user = self.user_from_token(token)
        if user is None:
            return None
        return [g.name for g in user.groups]

    def token_for(self, username, ip_address):
        """Create a new token for the given :param:`username`.

        :param username: A username to create token for.
        :param ip_address: IP address that used to retrieve this token.
        """
        user = self.dbsession.query(User).\
            filter(User.username == username).\
            one()

        user_session = UserSession(
            user=user,
            ip_address=ip_address,
            token=self._generate_token())

        self.dbsession.add(user_session)
        self.dbsession.flush()
        return user_session.token
