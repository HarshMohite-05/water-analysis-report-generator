from pathlib import Path
import pytest
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import database
from database.seed import seed
from components import report_preview
from services import dataset_service


def make_directory(tmp_path):
    employee_path = tmp_path / 'Employee Data.xlsx'
    client_path = tmp_path / 'Client Data.xlsx'
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(['Employee ID', 'Employee Name ', 'Role', 'Contact Number', 'Email ID', 'Password'])
    for row in [
        ['ADM001', 'Test Administrator', 'Admin', '123', 'admin@example.test', 'ChangeMe#1'],
        ['DIR1', 'Test Director', 'Director', '234', 'director@example.test', 'DirectorTest!'],
        ['TECH1', 'Assigned Technician', 'Technicion', '345', 'tech@example.test', 'TechTest!'],
        ['SALE1', 'Sales Person', 'Sales Executive', '456', 'sales@example.test', 'SalesTest!'],
    ]:
        sheet.append(row)
    workbook.save(employee_path)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(['Sr . No', 'Client Name', 'Office', 'Address', 'Contact Person', 'Technicin', 'Mail ID'])
    for i, (name, office) in enumerate([('Shree Prakash Textiles', 'Ahmedabad'), ('Mumbai Client', 'Mumbai')], 1):
        sheet.append([i, name, office, 'Fixture address', 'Contact', 'Assigned Technician', 'client@example.test'])
    workbook.save(client_path)
    return employee_path, client_path


@pytest.fixture
def isolated_reports(tmp_path, monkeypatch):
    from streamlit.runtime.pages_manager import PagesManager
    monkeypatch.setattr(PagesManager, 'uses_pages_directory', None)
    engine = create_engine(f'sqlite:///{tmp_path / "test.db"}', connect_args={'check_same_thread': False})
    monkeypatch.setattr(database, 'engine', engine)
    monkeypatch.setattr(database, 'SessionLocal', sessionmaker(bind=engine, expire_on_commit=False))
    monkeypatch.setattr(report_preview, 'TEMP_DIR', tmp_path / 'previews')
    monkeypatch.setattr(report_preview, 'GENERATED_DIR', tmp_path / 'reports')
    employee_path, client_path = make_directory(tmp_path)
    monkeypatch.setattr(dataset_service, 'EMPLOYEE_FILE', employee_path)
    monkeypatch.setattr(dataset_service, 'CLIENT_FILE', client_path)
    monkeypatch.setattr(dataset_service, 'BASE_DIR', tmp_path)
    monkeypatch.setattr(dataset_service, '_last_signature', None)
    seed()
    yield tmp_path
    engine.dispose()
