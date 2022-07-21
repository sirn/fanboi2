from pyramid.config import Configurator  # type: ignore


def includeme(config: Configurator):  # pragma: no cover
    config.include("fanboi2.core.auth")
    config.include("fanboi2.core.cache")
    config.include("fanboi2.core.geoip")
    config.include("fanboi2.core.redis")
    config.include("fanboi2.core.serializers")
    config.include("fanboi2.core.session")
    config.include("fanboi2.core.sqlalchemy")
    config.include("fanboi2.core.static")
