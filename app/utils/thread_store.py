# thread_store.py
from app.db.session import get_db
from app.models import EmailThreadInfo
from sqlalchemy import  Column, String, UniqueConstraint
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

def store_thread_info(thread_id: str, history_id: str, db: Session = Depends(get_db)) -> None:
    pass

def is_thread_id_stored(thread_id: str, db: Session = Depends(get_db)) -> bool:
    pass

def remove_thread_info(thread_id: str, db: Session = Depends(get_db)) -> None:
    pass