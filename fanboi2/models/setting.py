from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, JSON

from ._base import Base, Versioned


DEFAULT_SETTINGS = {
    'app.time_zone': 'UTC',
    'app.ident_size': 10,
    'ext.filters.akismet': None,
    'ext.filters.dnsbl': ('proxies.dnsbl.sorbs.net', 'xbl.spamhaus.org'),
    'ext.filters.proxy': {
        'blackbox': {
            'enabled': False,
            'url': 'http://proxy.mind-media.com/block/proxycheck.php',
        },
        'getipintel': {
            'enabled': False,
            'url':  'http://check.getipintel.net/check.php',
            'email': None,
            'flags': None,
        },
    }
}


class Setting(Versioned, Base):
    """Model class for various site settings."""

    __tablename__ = 'setting'

    key = Column(String, nullable=False, primary_key=True)
    value = Column(JSON)
