from logging.config import fileConfig
from alembic import context

# Importa tu engine y metadata
from config.db import engine, meta
from models import role, permission, role_permission, user

# Objeto de configuración de Alembic
config = context.config

# Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aquí indicas a Alembic qué metadata usar para autogenerar migraciones
target_metadata = meta


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = str(engine.url)  # Usa tu DATABASE_URL desde config.db
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
