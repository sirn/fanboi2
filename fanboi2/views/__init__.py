def includeme(config):  # pragma: no cover
    config.include("fanboi2.views.admin", route_prefix="/admin")
    config.include("fanboi2.views.api", route_prefix="/api")
    config.include("fanboi2.views.pages", route_prefix="/pages")
    config.include("fanboi2.views.boards", route_prefix="/")
    return config
