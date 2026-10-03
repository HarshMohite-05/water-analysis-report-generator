"""Initialize schema, parameter defaults, and the Excel-backed directory."""
from config.constants import DEFAULT_PARAMETERS
from database.database import init_db, session_scope
from database.models import Parameter
from services.template_service import ensure_templates


def seed():
    from services.cloud_bootstrap import restore_datasets
    restore_datasets()
    init_db()
    ensure_templates()
    with session_scope() as session:
        if session.query(Parameter).count() == 0:
            for i, (name, unit) in enumerate(DEFAULT_PARAMETERS, 1):
                session.add(Parameter(name=name, unit=unit, sort_order=i))
    from services.dataset_service import sync_directory
    sync_directory()


if __name__ == '__main__':
    seed()
    print('Database initialized from Excel datasets.')
