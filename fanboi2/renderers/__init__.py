from pyramid_jinja2.filters import route_path_filter

from .filters import (
    datetime_filter,
    format_page_filter,
    format_post_filter,
    format_post_ident_filter,
    format_post_ident_class_filter,
    isotime_filter,
    json_filter,
    merge_class_filter,
    static_path_filter,
    unquoted_path_filter,
)


def includeme(config):  # pragma: no cover
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("fanboi2:templates")

    def setup_jinja2_env():
        jinja2_env = config.get_jinja2_environment()
        jinja2_env.filters["datetime"] = datetime_filter
        jinja2_env.filters["isotime"] = isotime_filter
        jinja2_env.filters["json"] = json_filter
        jinja2_env.filters["merge_class"] = merge_class_filter
        jinja2_env.filters["page"] = format_page_filter
        jinja2_env.filters["format_post"] = format_post_filter
        jinja2_env.filters["format_post_ident"] = format_post_ident_filter
        jinja2_env.filters["format_post_ident_class"] = format_post_ident_class_filter
        jinja2_env.filters["route_path"] = route_path_filter
        jinja2_env.filters["static_path"] = static_path_filter
        jinja2_env.filters["unquoted_path"] = unquoted_path_filter

    config.action(None, setup_jinja2_env, order=999)

    return config
