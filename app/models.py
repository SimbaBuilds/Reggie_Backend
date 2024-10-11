from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, CheckConstraint, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.sql import func


Base = declarative_base()

class ThreadInfo(Base):
    __tablename__ = 'thread_info'

    thread_id = Column(String, primary_key=True)
    history_id = Column(String)

    __table_args__ = (
        UniqueConstraint('thread_id', name='unique_thread_id'),
    )


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    organization_name = Column(String(255), nullable=False)
    is_gsuite_user = Column(Boolean, nullable=False, default=False)
    subscription_type = Column(String(50), CheckConstraint("subscription_type IN ('free', 'digitize_only', 'full')"))
    digitization_complete = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    email_alias = Column(String(255), unique=True)

class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    gsuite_domain = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="organization")
    staff = relationship("Staff", back_populates="organization")

class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="students")

class Staff(Base):
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="staff")

class RecordProcessing(Base):
    __tablename__ = 'record_processing'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    original_filename = Column(String(255), nullable=False)
    status = Column(String(50), CheckConstraint("status IN ('pending', 'processing', 'uploaded', 'failed')"))
    error_message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    cloud_upload_path = Column(String(512))

    student = relationship("Student")
    staff = relationship("Staff")

class DigitizationJob(Base):
    __tablename__ = 'digitization_job'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    status = Column(String(50), CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'failed')"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User")

class EmailAutomation(Base):
    __tablename__ = 'email_automation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    label = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_triggered = Column(DateTime(timezone=True))
    total_emails_processed = Column(Integer, default=0)

    user = relationship("User")

class EmailTemplate(Base):
    __tablename__ = 'email_template'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(255), nullable=False)
    description = Column(String)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")

class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    action = Column(String(255), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(255))
    details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class UserUsage(Base):
    __tablename__ = 'user_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    date = Column(Date, nullable=False)
    emails_sent_to_reggie = Column(Integer, default=0)
    cumulative_files_processed = Column(Integer, default=0)
    miscellaneous_labeled_processed = Column(Integer, default=0)
    miscellaneous_unlabeled_processed = Column(Integer, default=0)
    records_requests_processed = Column(Integer, default=0)
    template_responses_processed = Column(Integer, default=0)

    user = relationship("User")

    __table_args__ = (
        CheckConstraint('user_id IS NOT NULL AND date IS NOT NULL', name='user_usage_user_id_date_check'),
    )


# Define the ThreadInfo model
class EmailThreadInfo(Base):
    __tablename__ = 'email_thread_info'

    thread_id = Column(String, primary_key=True)
    history_id = Column(String)

    __table_args__ = (
        UniqueConstraint('thread_id', name='unique_thread_id'),
    )