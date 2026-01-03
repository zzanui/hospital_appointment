from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import get_settings

settings = get_settings()

class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.db_url,
    future=True,
    echo=True, # 개발용: 쿼리 로깅
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def get_db() -> Generator:
    """
    FastAPI에서 DB 세션을 주입(Depends)받을 때 쓰는 함수
    요청이 끝나면 close됨
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    개발 편의용: 테이블이 없으면 생성
    """
    from core.models import Doctor  # 모델 import로 테이블 등록
    Base.metadata.create_all(bind=engine)
