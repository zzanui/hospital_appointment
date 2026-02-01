# 🏥 Hospital Async Appointment System

FastAPI 기반의 **비동기 병원 예약 시스템 백엔드 프로젝트**입니다.  
Admin / Patient API를 분리한 MSA 구조로 설계되었으며,  
**HTTP 202 + Job 패턴과 Outbox + Worker 구조**를 통해 대용량 예약 요청을 안정적으로 처리합니다.

---

## 1. 프로젝트 개요

- 병원 예약 도메인을 기반으로 한 비동기 백엔드 API 서버
- 관리자(Admin)는 의사 / 시술 / 병원 슬롯을 관리
- 환자(Patient)는 로그인 후 예약 가능 시간 조회 및 예약 생성
- 모든 예약 생성 요청은 **비동기 방식(202 + job_id)** 으로 처리
- API Gateway를 통해 모든 요청을 단일 진입점으로 수신

---

## 2. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL (운영), SQLite (테스트) |
| Async Pattern | HTTP 202 + Job, Outbox Pattern |
| Test | pytest (통합 테스트) |
| Package Manager | uv |
| Infra | Docker, Docker Compose |

---

## 3. 아키텍처

```text
Client
  │
  ▼
API Gateway (8000)
  ├── Patient API (8001)
  ├── Admin API (8002)
  └── Worker (Outbox Polling)
        │
        ▼
   PostgreSQL
   ├─ jobs
   ├─ outbox_events
   ├─ appointments
   ├─ hospital_slots
   └─ doctors / treatments
```

---

## 4. 실행 방법

### 4-1. 환경 변수

`.env.development` 예시:

```env
POSTGRES_USER=derm
POSTGRES_PASSWORD=derm
POSTGRES_DB=derm_clinic_dev
DATABASE_URL=postgresql+psycopg2://derm:derm@db:5432/derm_clinic_dev
```

### 4-2. Docker Compose 실행

```bash
docker compose up --build
```

- Gateway: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

---

## 5. API 구조

### 5-1. Admin API

Base URL: `/api/v1/admin`

| 기능 | Method | Endpoint |
|---|---|---|
| 의사 관리 | CRUD | /doctors |
| 시술 관리 | CRUD | /treatments |
| 병원 슬롯 관리 | CRUD | /hospital-slots |
| 통계 조회 | GET | /stats |

---

### 5-2. Patient API

Base URL: `/api/v1/patient`

| 기능 | Method | Endpoint |
|---|---|---|
| 로그인 | POST | /auth/patient/login |
| 의사 조회 | GET | /doctors |
| 예약 가능 시간 조회 | GET | /availability/{doctor_id}/availability |
| 예약 생성 (비동기) | POST | /appointments |
| Job 상태 조회 | GET | /jobs/{job_id} |
| 예약 목록 | GET | /appointments |
| 예약 취소 | PATCH | /appointments/{id}/cancel |

---

## 6. 비동기 예약 처리 흐름

1. 환자가 예약 생성 요청  
   `POST /api/v1/patient/appointments` → **202 Accepted**

2. 서버는 즉시 `job_id` 반환

3. Outbox 이벤트 저장

4. Worker가 Outbox 이벤트 polling

5. 실제 예약 생성 처리

6. Job 상태 변경  
   `QUEUED → RUNNING → SUCCEEDED / FAILED`

---

## 7. 주요 비즈니스 규칙

- 예약 시작 시간은 **15분 단위**
- 병원 슬롯은 **30분 단위 + 최대 수용 인원 제한**
- 점심시간(12:00~13:00) 예약 불가
- 동일 시간대 중복 예약 불가
- 시술 시간(`duration_minutes`)은 **30분 이상**

---

## 8. 테스트 전략

- pytest 기반 통합 테스트
- SQLite in-memory DB 사용
- `uv run pytest` 한 줄로 전체 테스트 실행
- conftest.py 수정 없이 테스트 코드만 작성
- 엔드포인트별 정상/예외 시나리오 구성

```bash
uv run pytest
```

---

## 9. 문제 해결 및 설계 고민

- PostgreSQL 시퀀스 불일치 문제 해결
- UNIQUE 제약 충돌로 인한 테스트 간섭 방지
- FastAPI 구조 설계 시 책임 경계 명확화
- 예약 가능 시간 계산을 백엔드 로직으로 처리
- JWT 기반 환자 인증 도입으로 개인정보 보호 강화

---

## 10. AI 활용 범위

- 코드 작성 및 패턴 참고
- 아키텍처 설계 보조
- 요구사항 분석 및 테스트 시나리오 구성
- README 문서 구조 정리

AI는 생산성 향상을 위한 도구로 활용되었으며,  
**설계 판단과 최종 구현 책임은 개발자 본인이 수행**했습니다.

---

## 11. 마무리

본 프로젝트는 단순 CRUD 과제를 넘어  
**비동기 처리, 데이터 정합성, 확장 가능한 구조**에 대한 고민을 담은 프로젝트입니다.

향후 Kafka 기반 이벤트 처리, 재시도 전략, 모니터링 도입 등으로 확장 가능한 구조를 목표로 설계되었습니다.

감사합니다 🙇‍♂️
