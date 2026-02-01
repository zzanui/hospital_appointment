# Hospital Async Reservation Platform (merged)

`hospital_appointment`(도메인 완성도) + `hospital-platform`(비동기/Outbox/Job 패턴)을 합친 통합 버전.

## Run (Docker)

```bash
docker compose up --build
```

- Gateway: http://localhost:8000
- Patient API: http://localhost:8001 (개발 단계에서 직접 노출)
- Admin API: http://localhost:8002 (개발 단계에서 직접 노출)

## Async 예약 생성 흐름

1) (로그인 후) 비동기 예약 접수

`POST /api/v1/patient/appointments/async`  -> `202 Accepted`

응답: `{ "job_id": "..." }`

2) Job 상태 확인

`GET /api/v1/patient/jobs/{job_id}`

- `QUEUED` -> `RUNNING` -> `SUCCEEDED` 또는 `FAILED`

3) Worker가 outbox_events를 polling하여 실제 예약을 생성

- 성공 시 `jobs.result = "appointment_id=..."`

## 기존 동기 API도 유지

- `POST /api/v1/patient/appointments` 는 기존 과제 스펙 그대로 동기 생성(201)
