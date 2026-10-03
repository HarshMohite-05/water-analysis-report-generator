from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(20), default="technician", nullable=False)
    default_office = Column(String(50), default="Mumbai Office")
    contact_number = Column(String(80), default="")
    password_hash = Column(String(300), nullable=False)
    active = Column(Boolean, default=True)


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    address = Column(Text, default="")
    contact_person = Column(String(120), default="")
    office = Column(String(50), default="")
    email = Column(String(200), default="")
    assigned_technician = Column(String(120), default="")
    assigned_employee_id = Column(String(50), ForeignKey("users.employee_id"), nullable=True)
    active = Column(Boolean, default=True)


class Parameter(Base):
    __tablename__ = "parameters"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    unit = Column(String(30), default="")
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    report_no = Column(String(40), unique=True)
    office = Column(String(50), nullable=False)
    client_name = Column(String(200), nullable=False)
    status = Column(String(20), default="draft")  # draft | final
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data = Column(JSON, nullable=False)  # full payload, see report_service
    pdf_path = Column(String(500), default="")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    action = Column(String(60), nullable=False)
    detail = Column(Text, default="")