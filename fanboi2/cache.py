import hashlib
import logging
from dogpile.cache import make_region
from jinja2 import nodes
from jinja2.ext import Extension


log = logging.getLogger(__name__)


def _key_mangler(key):
    """Retrieve cache keys as long concenated strings and turn them into
    an MD5 hash.
    """
    return hashlib.md5(bytes(key.encode('utf8'))).hexdigest()

cache_region = make_region(key_mangler=_key_mangler)


class Jinja2CacheExtension(Extension):
    """A Jinja2 :class:`Extension` that implements ``cache`` tag for template
    fragment caching using :module:`dogpile.cache`."""
    tags = set(['cache'])

    def __init__(self, environment):
        super(Jinja2CacheExtension, self).__init__(environment)
        environment.extend(cache_region=None, cache_expire=None)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [nodes.Const(parser.name), parser.parse_expression()]
        while parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        body = parser.parse_statements(['name:endcache'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_cache', args),
                               [], [], body).set_lineno(lineno)

    def _cache(self, *args, caller=None):
        """Retrieve data of provided key from dogpile cache region or
        store the value of ``cache`` block if cache does not exists.
        """
        if self.environment.cache_region is not None:
            key = "jinja2:%s" % ':'.join([str(a) for a in args])
            log.info("Template cache: %s" % key)
            return cache_region.get_or_create(key, caller,
                                              self.environment.cache_expire)
        return caller()
