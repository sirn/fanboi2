from pyramid.config import Configurator  # type: ignore
from pyramid.csrf import SessionCSRFStoragePolicy  # type: ignore


def includeme(config: Configurator):
    config.set_csrf_storage_policy(SessionCSRFStoragePolicy(key="_csrf"))
