import hashlib

from dogpile.cache import make_region  # type: ignore
from pyramid.config import Configurator  # type: ignore


def key_mangler(key: str) -> str:
    """
    Convert a concatenated strings of a hash key and turn them into
    an SHA256 hash.
    """
    return hashlib.sha256(bytes(key.encode("utf8"))).hexdigest()


def includeme(config: Configurator):  # pragma: no cover
    cache_region = make_region(key_mangler=key_mangler)
    cache_region.configure_from_config(config.registry.settings, "dogpile.")

    def cache_region_factory(context, request):
        return cache_region

    config.register_service_factory(cache_region_factory, name="cache")
