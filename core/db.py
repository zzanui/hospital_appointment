from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import get_settings
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass

_engine = None
_SessionLocal = None

def make_engine():
    settings = get_settings()
    db_url = settings.db_url

    #테스트환경에서는 sqlite in-memory DB 사용
    if db_url.startswith("sqlite") and ":memory:" in db_url:
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(db_url, pool_pre_ping=True)
        

def get_engine():
    global _engine
    if _engine is None:
        _engine = make_engine()
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=get_engine(),
        )
    return _SessionLocal



def get_db() -> Generator:
    """
    FastAPI에서 DB 세션을 주입(Depends)받을 때 쓰는 함수
    요청이 끝나면 close됨
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    개발 편의용: 테이블이 없으면 생성
    """
    from core import models
    Base.metadata.create_all(bind=get_engine())