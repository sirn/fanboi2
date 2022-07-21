import geoip2.database as geoip_db
from pyramid.config import Configurator  # type: ignore


def includeme(config: Configurator):  # pragma: no cache
    geoip_path = config.registry.settings["geoip.path"]
    if not geoip_path:
        return

    geoip = geoip_db.Reader(geoip_path)

    def geoip_factory(context, request):
        return geoip

    config.register_service_factory(geoip, name="geoip")
