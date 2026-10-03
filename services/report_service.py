from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from config.constants import DATE_FMT
from database.database import session_scope
from database.models import Client, Report, User
from services import audit_service
from utils.validators import validate_report_payload


# ---- clients -------------------------------------------------------------
def list_clients() -> List[dict]:
    from services.dataset_service import sync_directory
    sync_directory()
    with session_scope() as s:
        users = {u.employee_id: u for u in s.query(User).filter(User.active.is_(True))}
        result = []
        for c in s.query(Client).filter(Client.active.is_(True)).order_by(Client.name):
            employee = users.get(c.assigned_employee_id)
            result.append(dict(id=c.id, name=c.name, address=c.address, contact_person=c.contact_person,
                               office=c.office, email=c.email, assigned_technician=c.assigned_technician,
                               assigned_employee_id=c.assigned_employee_id,
                               assigned_employee_email=employee.email if employee else ""))
        return result


def upsert_client(name: str, address: str, contact_person: str, *, user_id: int,
                  office: str, email: str, assigned_employee_id: str) -> None:
    """Directory writes use the same Excel-backed authority as the Admin Panel."""
    from services.dataset_service import save_client
    save_client(user_id, dict(name=name, address=address, contact_person=contact_person,
                             office=office, email=email, assigned_employee_id=assigned_employee_id))


# ---- payload <-> JSON ----------------------------------------------------
def _ser(data: Dict) -> Dict:
    d = dict(data)
    for k in ("collection_date", "received_date", "analysis_date"):
        if isinstance(d.get(k), (date, datetime)):
            d[k] = d[k].strftime(DATE_FMT)
    return d


def _de(data: Dict) -> Dict:
    d = dict(data)
    for k in ("collection_date", "received_date", "analysis_date"):
        if isinstance(d.get(k), str):
            d[k] = datetime.strptime(d[k], DATE_FMT).date()
    return d


def _next_report_no(s, office_key: str) -> str:
    prefix = f"NWT/{office_key[:3].upper()}/{date.today():%y%m}/"
    n = s.query(Report).filter(Report.report_no.like(prefix + "%")).count() + 1
    return f"{prefix}{n:04d}"


# ---- reports -------------------------------------------------------------
def save_report(data: Dict, user_id: int, report_id: Optional[int] = None,
                status: str = "draft", pdf_path: str = "") -> int:
    """Payload keys: office, client_name, client_address, contact_person,
    collection_date, analysis_date, technician, sample_columns[list],
    parameters[list of {name, unit, values{col: str}}], remark_raw, remark_final."""
    from services.template_service import office_key

    payload = _ser(data)
    with session_scope() as s:
        if report_id:
            r = s.get(Report, report_id)
        else:
            r = Report(created_by=user_id, report_no=_next_report_no(s, office_key(data["office"])))
            s.add(r)
        r.office, r.client_name, r.status = data["office"], data["client_name"], status
        r.data = payload
        if pdf_path:
            r.pdf_path = pdf_path
        s.flush()
        rid = r.id
    audit_service.log(user_id, f"report_{status}", f"id={rid}")
    return rid


def get_report(report_id: int) -> Optional[dict]:
    with session_scope() as s:
        r = s.get(Report, report_id)
        if not r:
            return None
        return dict(id=r.id, report_no=r.report_no, status=r.status, pdf_path=r.pdf_path,
                    created_at=r.created_at, data=_de(r.data))


def list_reports(user_id: Optional[int] = None, limit: int = 200) -> List[dict]:
    with session_scope() as s:
        q = s.query(Report)
        if user_id is not None:
            q = q.filter(Report.created_by == user_id)
        return [dict(id=r.id, report_no=r.report_no, office=r.office, client=r.client_name,
                     status=r.status, created_at=r.created_at, pdf_path=r.pdf_path)
                for r in q.order_by(Report.id.desc()).limit(limit)]


def validate(data: Dict) -> List[str]:
    return validate_report_payload(data)