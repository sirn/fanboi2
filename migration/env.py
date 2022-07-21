import logging

from alembic import context  # type: ignore
from sqlalchemy import engine_from_config, pool

from fanboi2 import setup_logger
from fanboi2.models import Base
from fanboi2.settings import settings_from_env

settings = settings_from_env()


# Logger

setup_logger(settings)

log_level = logging.WARN
if settings["server.development"]:
    log_level = logging.INFO

logger = logging.getLogger("sqlalchemy.engine.base.Engine")
logger.setLevel(log_level)


# SQLAlchemy

target_metadata = Base.metadata
config = context.config
config.set_main_option("sqlalchemy.url", settings["sqlalchemy.url"])


def run_migrations_offline():
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in online mode."""
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    context.configure(connection=connection, target_metadata=target_metadata)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
