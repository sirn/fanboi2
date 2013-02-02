import isodate
import pytz
from pyramid.threadlocal import get_current_registry


def format_text(text):
    return text


def format_datetime(dt):
    registry = get_current_registry()
    timezone = pytz.timezone(registry.settings['app.timezone'])
    return dt.astimezone(timezone).strftime('%b %d, %Y at %H:%M:%S')


def format_isotime(dt):
    return isodate.datetime_isoformat(dt.astimezone(pytz.utc))