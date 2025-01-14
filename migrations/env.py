# migrations/env.py
from importlib import import_module
from logging.config import fileConfig
from alembic import context
from alchemical.alembic.env import run_migrations
from main import app

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# import the application's Alchemical instance
try:
    import_mod, db_name = config.get_main_option("alchemical_db", "").split(":")
    print(f"db_name: {db_name}")
    print(f"import_mod: {import_mod}")
    db = getattr(import_module(import_mod), db_name)
    print(f"db: {db}")
except (ModuleNotFoundError, AttributeError):
    raise ValueError(
        "Could not import the Alchemical database instance. "
        "Ensure that the alchemical_db setting in alembic.ini is correct."
    )

# run the migration engine
run_migrations(
    db,
    {
        "render_as_batch": True,
        "compare_type": True,
    },
)
