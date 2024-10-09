from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ThreadInfo(Base):
    __tablename__ = 'thread_info'

    thread_id = Column(String, primary_key=True)
    history_id = Column(String)

    __table_args__ = (
        UniqueConstraint('thread_id', name='unique_thread_id'),
    )