from .akismet import Akismet
from .dnsbl import Dnsbl
from .geoip import GeoIP
from .proxy import ProxyDetector
from .rate_limiter import RateLimiter
from .checklist import Checklist
from .request import serialize_request


dnsbl = Dnsbl()
akismet = Akismet()
proxy_detector = ProxyDetector()
geoip = GeoIP()
checklist = Checklist()
