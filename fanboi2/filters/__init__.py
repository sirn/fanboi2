from typing import Any, Callable, Dict, Optional

import venusian  # type: ignore
from pyramid.config import Configurator  # type: ignore

Services = Optional[Dict[str, Callable]]
Payload = Dict[str, Any]


def register_filter(name: str) -> Callable:  # pragma: no cover
    def _wrapped(cls: Callable):
        def callback(scanner: venusian.Scanner, _obj_name: str, obj: Callable):
            registry = scanner.config.registry
            registry["filters"].append((name, obj))

        venusian.attach(cls, callback)
        return cls

    return _wrapped


def includeme(config: Configurator):  # pragma: no cover
    config.registry.setdefault("filters", [])
    config.scan()
