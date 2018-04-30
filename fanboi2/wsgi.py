from . import settings_from_env, setup_logger, make_config

settings = settings_from_env()
setup_logger(settings)
config = make_config(settings)

app = config.make_wsgi_app()
