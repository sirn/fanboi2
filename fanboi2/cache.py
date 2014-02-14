import hashlib
import logging
from dogpile.cache import make_region


log = logging.getLogger(__name__)


def _key_mangler(key):
    """Retrieve cache keys as a long concatenated strings and turn them into
    an MD5 hash.

    :param key: A cache key :type:`str`.

    :type key: str
    :rtype: str
    """
    return hashlib.md5(bytes(key.encode('utf8'))).hexdigest()

cache_region = make_region(key_mangler=_key_mangler)
