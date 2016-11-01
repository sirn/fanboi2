from .akismet import Akismet
from .dnsbl import Dnsbl
from .proxy import ProxyDetector
from .rate_limiter import RateLimiter
from .request import serialize_request


dnsbl = Dnsbl()
akismet = Akismet()
proxy_detector = ProxyDetector()
