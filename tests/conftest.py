import sys
from pathlib import Path

# 어디서 pytest를 실행하든 core/apps import 가능하게
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import os
import pytest
from datetime import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import httpx

# 테스트 환경변수 
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DB_URL", "sqlite+pysqlite:///:memory:")
# gateway가 생성하는 upstream URL의 host와 conftest의 분기(host)가 일치해야 함
os.environ.setdefault("PATIENT_API_URL", "http://patient_api")
os.environ.setdefault("ADMIN_API_URL", "http://admin_api")

from core.db import Base, get_db as core_get_db  # noqa: E402
from apps.patient_api.main import app as patient_app  # noqa: E402
from apps.admin_api.main import app as admin_app  # noqa: E402
from apps.gateway.main import app as gateway_app  # noqa: E402

# 모델 import로 metadata 등록
from core.models import Doctor, Treatment, HospitalSlot, Patient  # noqa: E402


@pytest.fixture(scope="function")
def engine():
    """
    [요구사항 5-3] 테스트는 운영 DB와 분리된 in-memory SQLite 사용.
    StaticPool을 써야 connection이 바뀌어도 같은 in-memory DB를 유지함.
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def tables(engine):
    """
    테스트 세션 동안 테이블 생성/종료 시 drop.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine, tables):
    # ✅ 테스트마다 "같은 DB"를 쓰되, 바깥 트랜잭션을 걸어두고 끝나면 롤백해서 원복
    connection = engine.connect()
    trans = connection.begin()  # 바깥 트랜잭션

    SessionLocal = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    db = SessionLocal()

    # ✅ nested transaction (SAVEPOINT)
    db.begin_nested()

    # 앱 코드에서 db.commit()을 호출해도 테스트 격리가 유지되도록 SAVEPOINT를 다시 열어줌
    @event.listens_for(db, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield db
    finally:
        db.close()
        trans.rollback()      # ✅ 테스트 끝나면 전부 원복
        connection.close()


@pytest.fixture()
def override_db(db_session):
    """
    Patient/Admin API의 get_db를 테스트 세션으로 override.
    Gateway는 upstream으로 프록시하므로 upstream 앱의 get_db override가 중요.
    """
    def _override_get_db():
        yield db_session

    patient_app.dependency_overrides[core_get_db] = _override_get_db
    admin_app.dependency_overrides[core_get_db] = _override_get_db
    yield
    patient_app.dependency_overrides.clear()
    admin_app.dependency_overrides.clear()


@pytest.fixture()
def gateway_client(monkeypatch, override_db):
    """
    [통합테스트] gateway -> (patient/admin) 프록시를
    실제 네트워크 없이 ASGITransport로 연결하여 테스트한다.
    """
    patient_transport = httpx.ASGITransport(app=patient_app)
    admin_transport = httpx.ASGITransport(app=admin_app)

    class MultiAppTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            host = request.url.host
            if host == "patient_api":
                return await patient_transport.handle_async_request(request)
            if host == "admin_api":
                return await admin_transport.handle_async_request(request)
            raise RuntimeError(f"Unknown upstream host in tests: {host}")

    real_async_client = httpx.AsyncClient

    def patched_async_client(*args, **kwargs):
        kwargs["transport"] = MultiAppTransport()
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

    with TestClient(gateway_app) as c:
        yield c


@pytest.fixture()
def seed_master(db_session):
    """
    [테스트용 시드]
    - dev에서는 seed.sql로 데이터가 있지만,
      test(SQLite in-memory)에서는 데이터가 없으므로 테스트가 의존하는 최소 데이터만 주입.
    - login은 '조회' 동작이 안전하므로(오타 생성 방지),
      환자 데이터는 여기서 미리 생성해둔다.
    """
    d1 = Doctor(name="김원장", department="피부과")
    t1 = Treatment(name="여드름 치료", duration_minutes=30, price=10000, description="기본 여드름 치료")
    db_session.add_all([d1, t1])
    db_session.flush()
    db_session.refresh(d1)
    db_session.refresh(t1)

    # HospitalSlot: 09:00~18:00 30분 단위(점심 12~13 제외) 예시
    slots = []
    h, m = 9, 0
    while True:
        start = time(h, m)
        nm = m + 30
        nh = h
        if nm >= 60:
            nm -= 60
            nh += 1
        end = time(nh, nm)

        # 점심시간 제외
        if not (start >= time(12, 0) and end <= time(13, 0)):
            slots.append(HospitalSlot(start_time=start, end_time=end, max_capacity=2))

        h, m = nh, nm
        if h == 18 and m == 0:
            break

    # ✅ 테스트에서 로그인할 환자들 미리 생성 (login에서 생성하지 않기 위함)
    patients = [
        Patient(name="홍길동", phone_number="010-1111-2222"),
        Patient(name="김철수", phone_number="010-3333-4444"),
        Patient(name="박영희", phone_number="010-5555-6666"),
    ]

    db_session.add_all(slots)
    db_session.add_all(patients)
    db_session.flush()

    return {"doctor": d1, "treatment": t1, "patients": patients}


@pytest.fixture()
def auth_header(gateway_client, seed_master):
    """
    [헬퍼] 테스트에서 인증 헤더를 쉽게 얻기 위한 fixture.
    - seed_master가 선행되어 환자가 존재해야 login이 성공한다.
    """
    res = gateway_client.post(
        "/api/v1/patient/auth/patient/login",
        json={"phone_number": "010-3333-4444", "name": "김철수"},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
