# # tests/test_patient.py
# from __future__ import annotations

# from datetime import date, datetime, timedelta
# from uuid import uuid4


# # -------------------------
# # Auth: POST /api/v1/patient/auth/patient/login
# # -------------------------
# def test_patient_login_success(gateway_client, seed_master):
#     """
#     [정상 시나리오]
#     - 요구사항: 테스트에서 실제 로그인 → 토큰 발급 흐름을 사용해야 함.
#     - conftest.seed_master에 '김철수(010-3333-4444)'가 미리 생성되어 있으므로 로그인 성공이 보장된다.
#     """
#     res = gateway_client.post(
#         "/api/v1/patient/auth/patient/login",
#         json={"phone_number": "010-3333-4444", "name": "김철수"},
#     )
#     assert res.status_code == 200, res.text
#     body = res.json()
#     assert body["token_type"] == "bearer"
#     assert isinstance(body["access_token"], str) and body["access_token"]


# def test_patient_login_fail_when_not_found(gateway_client, seed_master):
#     """
#     [예외 시나리오]
#     - DB에 없는 환자는 로그인 실패(404)
#     - 이유: 로그인 요청이 곧 환자 생성으로 이어지면 오타/중복으로 데이터가 오염될 수 있어 위험.
#     """
#     res = gateway_client.post(
#         "/api/v1/patient/auth/patient/login",
#         json={"phone_number": f"010-{uuid4().hex[:4]}-{uuid4().hex[4:8]}", "name": "없는사람"},
#     )
#     assert res.status_code == 404, res.text


# # -------------------------
# # Doctors: GET /api/v1/patient/doctors
# # -------------------------
# def test_patient_list_doctors_success(gateway_client, seed_master):
#     """
#     [정상 시나리오]
#     - 환자 기능: 의사 목록 조회 200
#     - 이유: 예약 전 단계에서 의사 선택은 핵심 플로우이므로 항상 안정적으로 동작해야 함.
#     """
#     res = gateway_client.get("/api/v1/patient/doctors")
#     assert res.status_code == 200, res.text

#     body = res.json()
#     assert isinstance(body, list)
#     # seed_master에 doctor 1명이 있으므로 최소 1개 이상이어야 한다.
#     assert len(body) >= 1
#     assert "id" in body[0]
#     assert "department" in body[0]


# def test_patient_list_doctors_method_not_allowed(gateway_client):
#     """
#     [예외 시나리오]
#     - GET 전용 엔드포인트에 POST 요청 → 405
#     - 이유: Gateway 프록시 환경에서도 method 제한이 유지되는지 검증(오용 방지).
#     """
#     res = gateway_client.post("/api/v1/patient/doctors")
#     assert res.status_code == 405, res.text


# # -------------------------
# # Availability: GET /api/v1/patient/availability/{doctor_id}/availability
# # -------------------------
# def test_patient_availability_success(gateway_client, seed_master):
#     """
#     [정상 시나리오]
#     - 요구사항: 특정 의사의 예약 가능한 시작시간을 '15분 간격'으로 제공해야 함.
#     - 최소 검증: 200 + available_start_times(list) 존재 + 문자열 형태
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id
#     target_date = (date.today() + timedelta(days=1)).isoformat()

#     res = gateway_client.get(
#         f"/api/v1/patient/availability/{doctor_id}/availability",
#         params={"date": target_date, "treatment_id": treatment_id},
#     )
#     assert res.status_code == 200, res.text
#     body = res.json()

#     # Response 스키마 구현이 약간 달라도 핵심 필드는 반드시 있어야 함.
#     assert body.get("doctor_id") == doctor_id
#     assert body.get("treatment_id") == treatment_id
#     assert "available_start_times" in body
#     assert isinstance(body["available_start_times"], list)
#     if body["available_start_times"]:
#         assert isinstance(body["available_start_times"][0], str)


# def test_patient_availability_missing_query_422(gateway_client, seed_master):
#     """
#     [예외 시나리오]
#     - 필수 query(date, treatment_id) 누락 시 422
#     - 이유: 예약 가능 시간 계산은 날짜/시술이 필수 입력이므로 검증이 명확해야 함.
#     """
#     doctor_id = seed_master["doctor"].id
#     res = gateway_client.get(f"/api/v1/patient/availability/{doctor_id}/availability")
#     assert res.status_code == 422, res.text


# # -------------------------
# # Appointments Create: POST /api/v1/patient/appointments
# # -------------------------
# def test_patient_create_appointment_success(gateway_client, seed_master, auth_header):
#     """
#     [정상 시나리오]
#     - 마스터 데이터 + (로그인 토큰 보유) + 유효한 시작시간(15분 그리드) → 예약 생성 성공
#     - 중요: AppointmentCreate 스키마상 patient_name/patient_phone이 필수이므로 반드시 바디에 포함
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id

#     # 내일 10:00 (과거 시간 판정 방지)
#     start_dt = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

#     res = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,  # (현재 구현에서 사용하지 않더라도) 요구사항 충족을 위해 로그인 흐름을 포함
#         json={
#             "patient_name": "김철수",
#             "patient_phone": "010-3333-4444",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "통합테스트 예약",
#         },
#     )
#     assert res.status_code in (200, 201), res.text
#     body = res.json()
#     assert body["doctor_id"] == doctor_id
#     assert body["treatment_id"] == treatment_id
#     assert body["status"] in ("pending", "confirmed", "completed", "canceled")


# def test_patient_create_appointment_duplicate_same_doctor_same_time_fails(gateway_client, seed_master, auth_header):
#     """
#     [예외 시나리오]
#     - 요구사항: 동일 의사에게 동일 시간대 중복 예약 불가
#     - 1회 예약 성공 후 같은 의사/같은 시작시간으로 재요청하면 실패(400)해야 함.
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id
#     start_dt = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=15, second=0, microsecond=0)

#     first = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,
#         json={
#             "patient_name": "김철수",
#             "patient_phone": "010-3333-4444",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "첫 예약",
#         },
#     )
#     assert first.status_code in (200, 201), first.text

#     second = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,
#         json={
#             "patient_name": "김철수",
#             "patient_phone": "010-3333-4444",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "중복 예약",
#         },
#     )
#     # create_appointment가 ValueError를 400으로 감싸므로 400이 가장 자연스러움
#     assert second.status_code in (400, 409, 422), second.text


# # -------------------------
# # My Appointments: GET /api/v1/patient/appointments
# # -------------------------
# def test_patient_list_my_appointments_unauthorized(gateway_client, seed_master):
#     """
#     [예외 시나리오]
#     - 본인 예약 조회는 토큰 인증이 필수이므로 Authorization 없이 요청 시 401
#     """
#     res = gateway_client.get("/api/v1/patient/appointments")
#     assert res.status_code == 401, res.text


# def test_patient_list_my_appointments_success_after_create(gateway_client, seed_master, auth_header):
#     """
#     [정상 시나리오]
#     - 예약 1개 생성 후 내 예약 조회 시 최소 1개 이상 반환
#     - 이유: '본인 예약만 조회 가능' 요구사항을 충족하는지(조회 자체가 되는지) 검증
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id
#     start_dt = (datetime.now() + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)

#     create_res = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,
#         json={
#             "patient_name": "김철수",
#             "patient_phone": "010-3333-4444",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "조회용 예약",
#         },
#     )
#     assert create_res.status_code in (200, 201), create_res.text

#     res = gateway_client.get("/api/v1/patient/appointments", headers=auth_header)
#     assert res.status_code == 200, res.text
#     body = res.json()
#     assert isinstance(body, list)
#     assert len(body) >= 1


# # -------------------------
# # Cancel Appointment: PATCH /api/v1/patient/appointments/{appointment_id}/cancel
# # -------------------------
# def test_patient_cancel_appointment_success(gateway_client, seed_master, auth_header):
#     """
#     [정상 시나리오]
#     - 본인 예약을 cancel 엔드포인트로 취소하면 status=canceled로 변경
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id
#     start_dt = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)

#     created = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,
#         json={
#             "patient_name": "김철수",
#             "patient_phone": "010-3333-4444",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "취소 테스트",
#         },
#     )
#     assert created.status_code in (200, 201), created.text
#     appt_id = created.json()["id"]

#     res = gateway_client.patch(
#         f"/api/v1/patient/appointments/{appt_id}/cancel",
#         headers=auth_header,
#     )
#     assert res.status_code == 200, res.text
#     assert res.json()["status"] == "canceled"


# def test_patient_cancel_appointment_not_found_for_other_patient(gateway_client, seed_master, auth_header):
#     """
#     [예외 시나리오]
#     - 타인의 예약을 취소하려고 하면 404 (Appointment not found)
#     - 이유: '본인의 예약만 조회/변경 가능' 보안 요구사항 검증
#     """
#     doctor_id = seed_master["doctor"].id
#     treatment_id = seed_master["treatment"].id
#     start_dt = (datetime.now() + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)

#     # 홍길동 예약 생성 (auth는 김철수로 가져오지만, 생성 API는 body 기반이라 홍길동 예약이 생성됨)
#     created = gateway_client.post(
#         "/api/v1/patient/appointments",
#         headers=auth_header,
#         json={
#             "patient_name": "홍길동",
#             "patient_phone": "010-1111-2222",
#             "doctor_id": doctor_id,
#             "treatment_id": treatment_id,
#             "start_datetime": start_dt.isoformat(),
#             "memo": "타인 예약",
#         },
#     )
#     assert created.status_code in (200, 201), created.text
#     appt_id = created.json()["id"]

#     # 김철수 토큰으로 홍길동 예약 취소 시도 → 404
#     res = gateway_client.patch(
#         f"/api/v1/patient/appointments/{appt_id}/cancel",
#         headers=auth_header,
#     )
#     assert res.status_code == 404, res.text
