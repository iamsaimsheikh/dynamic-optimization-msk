import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import Config  # Absolute import for config

from database.db import engine, Base  
from database.models import * 

target_metadata = Base.metadata

def run_migrations_online():
    from sqlalchemy import pool
    from sqlalchemy.engine import create_engine
    from alembic import context

    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
