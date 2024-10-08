# thread_store.py

import os
from sqlalchemy import create_engine, Column, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found. Please set the DATABASE_URL environment variable.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Base class for declarative models
Base = declarative_base()

# Define the ThreadInfo model
class ThreadInfo(Base):
    __tablename__ = 'thread_info'

    thread_id = Column(String, primary_key=True)
    history_id = Column(String)

    __table_args__ = (
        UniqueConstraint('thread_id', name='unique_thread_id'),
    )

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Function to store thread info
def store_thread_info(thread_id, history_id):
    session = SessionLocal()
    try:
        thread_info = ThreadInfo(thread_id=thread_id, history_id=history_id)
        session.merge(thread_info)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error storing thread info: {e}")
    finally:
        session.close()

# Function to check if thread_id is stored
def is_thread_id_stored(thread_id):
    session = SessionLocal()
    try:
        exists = session.query(ThreadInfo).filter(ThreadInfo.thread_id == thread_id).first() is not None
        return exists
    except Exception as e:
        print(f"Error checking thread info: {e}")
        return False
    finally:
        session.close()

# Function to remove thread info
def remove_thread_info(thread_id):
    session = SessionLocal()
    try:
        thread_info = session.query(ThreadInfo).filter(ThreadInfo.thread_id == thread_id).first()
        if thread_info:
            session.delete(thread_info)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error removing thread info: {e}")
    finally:
        session.close()