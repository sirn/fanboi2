from pyramid.config import Configurator  # type: ignore
from pyramid.request import Request  # type: ignore


def route_name(request: Request):
    """Returns :attr:`name` of current :attr:`request.matched_route`."""
    if request.matched_route:
        return request.matched_route.name


def includeme(config: Configurator):  # pragma: no cover
    config.add_request_method(route_name, property=True)
