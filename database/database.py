from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope():
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def init_db() -> None:
    from database import models  # noqa: F401  (register tables)

    Base.metadata.create_all(engine)
    # Additive migration: preserve existing reports and their user/client IDs.
    additions = {
        "users": {"contact_number": "VARCHAR(80) DEFAULT ''"},
        "clients": {"office": "VARCHAR(50) DEFAULT ''", "email": "VARCHAR(200) DEFAULT ''",
                    "assigned_technician": "VARCHAR(120) DEFAULT ''",
                    "assigned_employee_id": "VARCHAR(50) REFERENCES users(employee_id)",
                    "active": "BOOLEAN DEFAULT 1"},
    }
    with engine.begin() as connection:
        for table, fields in additions.items():
            existing = {c["name"] for c in inspect(connection).get_columns(table)}
            for field, definition in fields.items():
                if field not in existing:
                    connection.execute(text(f'ALTER TABLE {table} ADD COLUMN {field} {definition}'))