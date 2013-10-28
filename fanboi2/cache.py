import hashlib
from dogpile.cache import make_region


def _key_mangler(key):
    """Retrieve cache keys as long concenated strings and turn them into
    an MD5 hash.
    """
    return hashlib.md5(bytes(key.encode('utf8'))).hexdigest()

cache_region = make_region(key_mangler=_key_mangler)
