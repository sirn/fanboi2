import json
import urllib
import isodate
import pytz
from jinja2 import contextfilter

from ..interfaces import ISettingQueryService
from .formatters import (
    format_post,
    format_page,
    get_asset_hash,
    get_asset_hash_cached,
)


@contextfilter
def post_filter(ctx, post, shorten=False):
    """Exposes :func:`fanboi2.renderers.formatters.format_post` to Jinja2.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param post: A :class:`fanboi2.models.Post` object.
    :param shorten: An :type:`int` or :type:`None`.
    """
    request = ctx.get("request")
    return format_post(request, post, shorten)


@contextfilter
def page_filter(ctx, page):
    """Exposes :func:`fanboi2.renderers.formatters.format_page` to Jinja2.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param page: A :class:`fanboi2.models.Page` object.
    """
    request = ctx.get("request")
    return format_page(request, page)


@contextfilter
def datetime_filter(ctx, dt):
    """Format datetime into a human-readable format.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param dt: A :class:`datetime.datetime` object.
    """
    request = ctx.get("request")
    setting_query_svc = request.find_service(ISettingQueryService)
    tz = pytz.timezone(setting_query_svc.value_from_key("app.time_zone"))
    return dt.astimezone(tz).strftime("%b %d, %Y at %H:%M:%S")


@contextfilter
def isotime_filter(ctx, dt):
    """Format datetime into a machine-readable format.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param dt: A :class:`datetime.datetime` object.
    """
    return isodate.datetime_isoformat(dt.astimezone(pytz.utc))


@contextfilter
def json_filter(ctx, data):
    """Format the given data structure into JSON string.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param data: A data to format to JSON.
    """
    return json.dumps(data, indent=4, sort_keys=True)


@contextfilter
def unquoted_path_filter(ctx, *args, **kwargs):
    """Returns an unquoted path for specific arguments.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    """
    request = ctx.get("request")
    return urllib.parse.unquote(request.route_path(*args, **kwargs))


@contextfilter
def static_path_filter(ctx, path, **kwargs):
    """Exposes :func:`fanboi2.renderers.formatters.get_asset_hash` to Jinja2.

    :param ctx: A :class:`jinja2.runtime.Context` object.
    :param path: An asset specification to the asset file.
    :param kwargs: Arguments to pass to :meth:`request.static_path`.
    """
    request = ctx.get("request")
    if request.registry.settings.get("server.development"):  # pragma: no cover
        kwargs["_query"] = {"h": get_asset_hash(path)[:8]}
    else:
        kwargs["_query"] = {"h": get_asset_hash_cached(path)[:8]}
    return request.static_path(path, **kwargs)
