import logging
from typing import Dict, Union

from pyramid.config import Configurator  # type: ignore


def setup_logger(settings: Dict[str, Union[int, str, bool]]):  # pragma: no cover
    """Setup logger per configured in settings."""
    log_level = logging.WARN
    if settings["server.development"]:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s[%(process)d] %(message)s",
        datefmt="%H:%M:%S",
    )


def make_configurator(settings: Dict[str, Union[int, str, bool]]):  # pragma: no cover
    """Returns a Pyramid configurator."""
    with Configurator(settings=settings) as config:
        config.add_settings(
            {
                "mako.directories": "fanboi2:templates",
                "dogpile.backend": "dogpile.cache.redis",
                "dogpile.arguments.url": config.registry.settings["redis.url"],
                "dogpile.redis_expiration_time": 60 * 60 * 1,  # 1 hour
                "dogpile.arguments.distributed_lock": True,
            }
        )

        if config.registry.settings["server.development"]:
            config.add_settings(
                {
                    "pyramid.reload_templates": True,
                    "pyramid.debug_authorization": True,
                    "pyramid.debug_notfound": True,
                    "pyramid.default_locale_name": "en",
                    "debugtoolbar.hosts": "0.0.0.0/0",
                }
            )
            config.include("pyramid_debugtoolbar")

        config.include("pyramid_mako")
        config.include("pyramid_services")

        config.include("fanboi2.core")
        config.include("fanboi2.filters")
        config.include("fanboi2.helpers")
        config.include("fanboi2.services")
        config.include("fanboi2.tasks")

        config.include("fanboi2.views.admin", route_prefix="/admin")
        config.include("fanboi2.views.api", route_prefix="/api")
        config.include("fanboi2.views.pages", route_prefix="/pages")
        config.include("fanboi2.views.boards", route_prefix="/")

    return config
