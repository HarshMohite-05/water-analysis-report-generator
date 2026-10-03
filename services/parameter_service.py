from __future__ import annotations

from typing import List

from database.database import session_scope
from database.models import Parameter


def list_parameters(include_inactive: bool = False) -> List[dict]:
    with session_scope() as s:
        q = s.query(Parameter)
        if not include_inactive:
            q = q.filter(Parameter.active.is_(True))
        return [
            dict(id=p.id, name=p.name, unit=p.unit, active=p.active)
            for p in q.order_by(Parameter.sort_order, Parameter.name)
        ]


def add_parameter(name: str, unit: str) -> None:
    name = name.strip()
    if not name:
        raise ValueError("Parameter name is required.")
    with session_scope() as s:
        existing = s.query(Parameter).filter(Parameter.name.ilike(name)).first()
        if existing:
            existing.active, existing.unit = True, unit.strip()
            return
        n = s.query(Parameter).count()
        s.add(Parameter(name=name, unit=unit.strip(), sort_order=n + 1))


def update_parameter(pid: int, name: str, unit: str, active: bool) -> None:
    update_parameters([dict(id=pid, name=name, unit=unit, active=active)])


def update_parameters(rows: List[dict]) -> None:
    """Validate and save the entire editor in a single database transaction."""
    with session_scope() as s:
        parameters = {p.id: p for p in s.query(Parameter)}
        changes = {}
        for row in rows:
            pid = int(row['id'])
            if pid not in parameters:
                raise ValueError('A parameter no longer exists. Reload and try again.')
            name = str(row.get('name') or '').strip()
            if not name:
                raise ValueError('Parameter name is required.')
            changes[pid] = (name, str(row.get('unit') or '').strip(), bool(row['active']))
        names = [changes[pid][0].casefold() if pid in changes else p.name.casefold()
                 for pid, p in parameters.items()]
        if len(names) != len(set(names)):
            raise ValueError('Parameter names must be unique.')
        for pid, (name, unit, active) in changes.items():
            p = parameters[pid]
            p.name, p.unit, p.active = name, unit, active
