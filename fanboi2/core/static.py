import hashlib
from functools import lru_cache
from typing import Dict, Union

from pyramid.config import Configurator  # type: ignore
from pyramid.path import AssetResolver  # type: ignore
from pyramid.request import Request  # type: ignore


@lru_cache(maxsize=10)
def _get_asset_hash_cached(path: str):
    """Similar to :func:`_get_asset_hash` but the result is cached."""
    return _get_asset_hash(path)


def _get_asset_hash(path: str) -> str:
    """Returns an MD5 hash of the given assets path."""
    if ":" in path:
        package, path = path.split(":")
        resolver = AssetResolver(package)
    else:
        resolver = AssetResolver()
    fullpath = resolver.resolve(path).abspath()
    md5 = hashlib.md5()
    with open(fullpath, "rb") as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


def tagged_static_path_cached(
    request: Request,
    path: str,
    **kwargs: Dict[str, Union[int, str, bool]],
) -> str:
    """Similar to Pyramid's :func:`tagged_static_path` but the result is cached."""
    kwargs["_query"] = {"h": _get_asset_hash_cached(path)[:8]}
    return request.static_path(path, **kwargs)


def tagged_static_path(
    request: Request,
    path: str,
    **kwargs: Dict[str, Union[int, str, bool]],
) -> str:
    """
    Similar to Pyramid's :meth:`request.static_path` but append first 8
    characters of file hash as query string ``h`` to it forcing proxy server
    and browsers to expire cache immediately after the file is modified.
    """
    kwargs["_query"] = {"h": _get_asset_hash(path)[:8]}
    return request.static_path(path, **kwargs)


def includeme(config: Configurator):
    config.add_route("robots", "/robots.txt")

    if config.registry.settings["server.development"]:
        config.add_request_method(tagged_static_path, name="tagged_static_path")
        config.add_static_view("static", "fanboi2:static")
    else:
        config.add_request_method(tagged_static_path_cached, name="tagged_static_path")
        config.add_static_view("static", "fanboi2:static", cache_max_age=3600)
