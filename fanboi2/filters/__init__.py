import venusian


def register_filter(name):  # pragma: no cover

    def _wrapped(cls):

        def callback(scanner, obj_name, obj):
            registry = scanner.config.registry
            registry["filters"].append((name, obj))

        venusian.attach(cls, callback)
        return cls

    return _wrapped


def includeme(config):  # pragma: no cover
    config.registry.setdefault("filters", [])
    config.scan()
