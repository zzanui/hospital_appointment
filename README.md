# 🏥 Hospital Appointment System

FastAPI 기반의 **병원 예약 시스템 백엔드 과제**입니다.  
Admin / Patient API를 분리하고, Gateway를 통해 단일 진입점을 제공하는 구조로 설계되었습니다.

---

## 1. 프로젝트 개요

- 병원 예약을 위한 백엔드 API 서버
- 관리자(Admin)는 의사/시술/병원 슬롯을 관리
- 환자(Patient)는 로그인 후 예약 가능 시간 조회 및 예약/취소 가능
- API Gateway를 통해 모든 요청을 단일 엔드포인트로 처리

---

## 2. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| DB | PostgreSQL (실서비스), SQLite (테스트) |
| Test | pytest |
| Package Manager | uv |
| Infra | Docker, Docker Compose |

---

## 3. 아키텍처

```
Client
  │
  ▼
API Gateway (8000)
  ├── Patient API (8001)
  └── Admin API (8002)
        │
        ▼
   PostgreSQL
```

- Gateway는 요청 경로에 따라 Admin / Patient API로 프록시
- 각 API는 독립적인 FastAPI 앱으로 구성

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
| 의사 목록 | GET | /doctors |
| 의사 생성 | POST | /doctors |
| 의사 수정 | PUT | /doctors/{id} |
| 의사 삭제 | DELETE | /doctors/{id} |
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
| 예약 생성 | POST | /appointments |
| 예약 목록 | GET | /appointments |
| 예약 취소 | PATCH | /appointments/{id}/cancel |

---

## 6. 주요 비즈니스 규칙

- 예약 시작 시간은 **15분 단위**
- 병원 슬롯은 **30분 단위 + 최대 수용 인원 제한**
- 점심시간(12:00~13:00) 예약 불가
- 동일 시간대 중복 예약 불가
- 시술 시간(`duration_minutes`)은 **30분 이상**

---

## 7. 테스트 전략

- pytest 기반 통합 테스트
- `uv run pytest` 한 줄로 전체 테스트 실행
- conftest.py는 수정하지 않고 테스트 파일만 작성
- 테스트 DB(SQLite) 사용
- 엔드포인트별 **정상/예외 최소 2개 시나리오** 구성

```bash
uv run pytest
```

---

## 8. 수동 API 테스트

- Swagger UI (`/docs`) 또는 curl 기반 테스트 가능
- PowerShell 환경에서는 `curl.exe` 사용 권장
- JSON 요청은 파일(`.json`)로 만들어 `--data-binary` 사용

---

## 9. 문제 해결 기록 (요약)

- seed 데이터 사용 시 **PostgreSQL 시퀀스 불일치 문제** 해결
- UNIQUE 제약 충돌로 인한 테스트 간섭 방지
- Gateway OPTIONS / CORS 이슈 해결
- 스키마 필드명 불일치(start_time vs starttime 등) 통일

---

## 10. AI 활용 범위

본 프로젝트에서는 다음 영역에서 AI의 도움을 받았습니다.

- **코드 작성**: FastAPI, SQLAlchemy, pytest 사용 예시 및 패턴 참고
- **아키텍처 설계**: Admin / Patient API 분리, Gateway 구조 설계
- **요구사항 분석**: 과제 요구사항을 기능 단위로 분해
- **테스트 설계**: 정상/예외 시나리오 구성, 테스트 독립성 확보 전략
- **보고서(MD) 작성**: README 구조 정리 및 문서화 보조

AI는 학습과 구현 속도를 높이기 위한 도구로 활용되었으며, 최종적인 설계 판단과 구현 책임은 개발자 본인이 수행했습니다.

---

## 11. 개발 과정에서의 문제점과 해결

### 문제점

1. **개발 PC 사양 문제**  
   - 과제 테스트 환경에서 CPU / 메모리 사용률이 평균 90% 이상으로 상승

2. **FastAPI 디렉터리 구조에 대한 고민**  
   - FastAPI는 디렉터리 구조나 파일 분할 방식이 엄격히 정해져 있지 않아
   - 처음 사용하면서 프로젝트 구조 설계에 많은 고민 발생

3. **환경변수 로딩 정책으로 인한 DB 연결 실패**  
   - “선언되지 않은 환경변수는 허용하지 않는다”는 기본 정책으로 인해
   - 필요한 환경변수를 모두 선언하지 않아 DB 커넥션 오류 발생

4. **예약 가능 시간 계산 방식에 대한 설계 고민 (중요)**  
   - 예약 가능 시간은 15분 단위로 고정되어 있음
   - 이에 대해 다음 두 가지 방안을 고민함:
     - (1) 한 달치 15분 단위 데이터를 미리 DB에 적재하고 매일 업데이트
     - (2) 날짜 기준으로 비어 있는 예약 시간을 조회한 후, 백엔드에서 15분 단위로 분할하여 제공

5. **예약 정보의 개인정보 이슈**  
   - 예약 정보는 사용자의 개인정보에 해당
   - 단순히 이름, 전화번호를 파라미터로 전달하는 방식은 보안상 위험하다고 판단

---

### 해결 방법

1. **WSL 리소스 제한을 통한 개발 환경 안정화**  
   - `vmmem` 프로세스가 과도하게 메모리를 점유하는 문제 확인
   - `.wslconfig` 파일을 생성하여 CPU/메모리 사용량을 전체 사양의 1/4 수준으로 제한
   - 참고: https://blaxsior-repository.tistory.com/91

2. **MSA 관점에서의 디렉터리 구조 재정립**  
   - Admin / Patient / Gateway 앱 단위로 디렉터리 분리
   - FastAPI 구조 설계 시 AI의 도움을 받되, 서비스 책임 경계를 명확히 구분

3. **필요 환경변수 명시적 선언**  
   - DB 접속 및 서비스 실행에 필요한 환경변수를 모두 명시적으로 선언
   - 환경변수 누락으로 인한 런타임 오류 방지

4. **예약 시간 계산을 백엔드 로직으로 처리**  
   - DB에는 30분 단위 병원 슬롯과 최대 수용 인원만 저장
   - 15분 단위 예약 가능 여부는 백엔드에서 유효성 검증으로 처리
   - 이를 통해 DB 구조 단순화 및 비즈니스 규칙 변경에 대한 유연성 확보

5. **환자 세션 기반 인증 도입**  
   - 환자 로그인 시 세션 토큰(JWT) 발급
   - 인증된 사용자만 예약 조회/생성/취소 가능하도록 제한
   - 개인정보 보호 및 무단 접근 방지

---

## 12. 마무리

본 프로젝트는 AI의 도움을 받아 학습 곡선을 낮추고 구현을 완성했지만, 동시에 **AI 활용의 한계와 개발자로서의 주도성에 대해 깊이 고민하게 만든 경험**이었습니다.

요구사항을 단순히 만족시키는 데서 그치지 않고,
- 왜 이런 구조를 선택했는지
- 어떤 부분을 충분히 이해하지 못했는지
- 다음에는 어떻게 더 나은 선택을 할 수 있을지

를 돌아볼 수 있는 의미 있는 과제였습니다.

이 경험을 바탕으로, 이후 프로젝트에서는 **이해를 기반으로 한 설계와 구현**을 목표로 지속적으로 성장해 나가고자 합니다.

---

감사합니다 🙇‍♂️

