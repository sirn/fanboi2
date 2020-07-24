from pyramid_jinja2.filters import route_path_filter

from .filters import (
    datetime_filter,
    isotime_filter,
    json_filter,
    page_filter,
    post_filter,
    static_path_filter,
    unquoted_path_filter,
)


def includeme(config):  # pragma: no cover
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("fanboi2:templates")

    extra_template_path = config.registry.settings["template.path"]

    if extra_template_path is not None:
        config.add_jinja2_search_path(extra_template_path)

    def setup_jinja2_env():
        jinja2_env = config.get_jinja2_environment()
        jinja2_env.filters["datetime"] = datetime_filter
        jinja2_env.filters["isotime"] = isotime_filter
        jinja2_env.filters["json"] = json_filter
        jinja2_env.filters["page"] = page_filter
        jinja2_env.filters["post"] = post_filter
        jinja2_env.filters["route_path"] = route_path_filter
        jinja2_env.filters["static_path"] = static_path_filter
        jinja2_env.filters["unquoted_path"] = unquoted_path_filter

    config.action(None, setup_jinja2_env, order=999)

    return config
