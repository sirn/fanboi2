import binascii

from pyramid.config import Configurator  # type: ignore
from pyramid.csrf import SessionCSRFStoragePolicy  # type: ignore
from pyramid_nacl_session import EncryptedCookieSessionFactory  # type: ignore


def includeme(config: Configurator):
    session_secret_hex = config.registry.settings["session.secret"].strip()
    session_secret = binascii.unhexlify(session_secret_hex)
    session_factory = EncryptedCookieSessionFactory(
        session_secret, cookie_name="_session", timeout=3600, httponly=True
    )

    config.set_session_factory(session_factory)
    config.set_csrf_storage_policy(SessionCSRFStoragePolicy(key="_csrf"))
