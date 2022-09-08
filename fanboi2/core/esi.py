import logging

from pyramid.config import Configurator  # type: ignore
from pyramid.events import NewResponse  # type: ignore
from pyramid.request import Request  # type: ignore
from pyramid.response import Response  # type: ignore

logger = logging.getLogger(__name__)


def set_esi_header(event: NewResponse):
    """Sets the ESI Surrogate-Capability header."""
    request: Request = event.request
    response: Response = event.response

    if "Surrogate-Capability" in request.headers:
        surrogate = request.headers["Surrogate-Capability"]
        if "ESI/1.0" not in surrogate:
            return

    response.headers.add("Surrogate-Control", "content=ESI/1.0")


def includeme(config: Configurator):
    if config.registry.settings["server.esi"]:
        config.add_subscriber(set_esi_header, NewResponse)
