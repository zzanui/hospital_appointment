# tests/test_admin.py
from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4


# =========================================================
# Admin Doctors CRUD
# Base: /api/v1/admin/doctors
# =========================================================

def test_admin_create_doctor_success(gateway_client):
    """
    [정상] POST /api/v1/admin/doctors
    - 마스터 데이터(의사) 생성이 성공해야 이후 예약/통계 기능이 정상 동작함.
    """
    res = gateway_client.post(
        "/api/v1/admin/doctors",
        json={"name": f"의사-{uuid4().hex[:6]}", "department": "피부과"},
    )
    assert res.status_code in (200, 201), res.text
    body = res.json()
    assert "id" in body
    assert body["department"] == "피부과"


def test_admin_create_doctor_validation_fail_422(gateway_client):
    """
    [예외] POST /api/v1/admin/doctors
    - 필수값 누락은 422
    """
    res = gateway_client.post("/api/v1/admin/doctors", json={"department": "피부과"})
    assert res.status_code == 422, res.text


def test_admin_list_doctors_success(gateway_client):
    """
    [정상] GET /api/v1/admin/doctors
    """
    res = gateway_client.get("/api/v1/admin/doctors")
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


def test_admin_list_doctors_method_not_allowed_405(gateway_client):
    """
    [예외] GET 엔드포인트에 PATCH → 405
    """
    res = gateway_client.patch("/api/v1/admin/doctors")
    assert res.status_code == 405, res.text


def test_admin_get_doctor_success(gateway_client):
    """
    [정상] GET /api/v1/admin/doctors/{doctor_id}
    """
    created = gateway_client.post(
        "/api/v1/admin/doctors",
        json={"name": f"의사-{uuid4().hex[:6]}", "department": "정형외과"},
    )
    assert created.status_code in (200, 201), created.text
    doctor_id = created.json()["id"]

    res = gateway_client.get(f"/api/v1/admin/doctors/{doctor_id}")
    assert res.status_code == 200, res.text
    assert res.json()["id"] == doctor_id


def test_admin_get_doctor_not_found_404(gateway_client):
    """
    [예외] GET /api/v1/admin/doctors/{doctor_id} - 없는 리소스는 404
    """
    res = gateway_client.get("/api/v1/admin/doctors/999999")
    assert res.status_code == 404, res.text


def test_admin_update_doctor_success(gateway_client):
    """
    [정상] PUT /api/v1/admin/doctors/{doctor_id}
    - 응답에 is_active가 없을 수 있으므로 department 변경만 검증한다.
    """
    created = gateway_client.post(
        "/api/v1/admin/doctors",
        json={"name": f"의사-{uuid4().hex[:6]}", "department": "피부과"},
    )
    assert created.status_code in (200, 201), created.text
    doctor_id = created.json()["id"]

    res = gateway_client.put(
        f"/api/v1/admin/doctors/{doctor_id}",
        json={"department": "성형외과"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["department"] == "성형외과"


def test_admin_update_doctor_not_found_404(gateway_client):
    """
    [예외] PUT /api/v1/admin/doctors/{doctor_id} - 없는 리소스는 404
    """
    res = gateway_client.put("/api/v1/admin/doctors/999999", json={"department": "성형외과"})
    assert res.status_code == 404, res.text


def test_admin_delete_doctor_success_204(gateway_client):
    """
    [정상] DELETE /api/v1/admin/doctors/{doctor_id} -> 204
    """
    created = gateway_client.post(
        "/api/v1/admin/doctors",
        json={"name": f"의사-{uuid4().hex[:6]}", "department": "내과"},
    )
    assert created.status_code in (200, 201), created.text
    doctor_id = created.json()["id"]

    res = gateway_client.delete(f"/api/v1/admin/doctors/{doctor_id}")
    assert res.status_code == 204, res.text

    get_res = gateway_client.get(f"/api/v1/admin/doctors/{doctor_id}")
    assert get_res.status_code == 404, get_res.text


def test_admin_delete_doctor_not_found_404(gateway_client):
    """
    [예외] DELETE /api/v1/admin/doctors/{doctor_id} - 없는 리소스는 404
    """
    res = gateway_client.delete("/api/v1/admin/doctors/999999")
    assert res.status_code == 404, res.text


# =========================================================
# Admin Treatments CRUD
# Base: /api/v1/admin/treatments
# =========================================================

def test_admin_create_treatment_success(gateway_client):
    """
    [정상] POST /api/v1/admin/treatments
    """
    res = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 30,
            "price": 10000,
            "description": "기본 치료",
        },
    )
    assert res.status_code in (200, 201), res.text
    assert res.json()["duration_minutes"] == 30


def test_admin_create_treatment_invalid_duration_400(gateway_client):
    """
    [예외] POST /api/v1/admin/treatments
    - 25분은 스키마 레벨(ge>=30)에서 422일 수 있고, 서비스 검증에서 400일 수도 있음.
    """
    res = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 25,
            "price": 10000,
            "description": "실패해야 함",
        },
    )
    assert res.status_code in (400, 422), res.text


def test_admin_list_treatments_success(gateway_client):
    """
    [정상] GET /api/v1/admin/treatments
    """
    res = gateway_client.get("/api/v1/admin/treatments")
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


def test_admin_list_treatments_method_not_allowed_405(gateway_client):
    """
    [예외] GET 엔드포인트에 PATCH → 405
    """
    res = gateway_client.patch("/api/v1/admin/treatments")
    assert res.status_code == 405, res.text


def test_admin_get_treatment_success(gateway_client):
    """
    [정상] GET /api/v1/admin/treatments/{treatment_id}
    """
    created = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 60,
            "price": 20000,
            "description": "",
        },
    )
    assert created.status_code in (200, 201), created.text
    treatment_id = created.json()["id"]

    res = gateway_client.get(f"/api/v1/admin/treatments/{treatment_id}")
    assert res.status_code == 200, res.text
    assert res.json()["id"] == treatment_id


def test_admin_get_treatment_not_found_404(gateway_client):
    """
    [예외] GET /api/v1/admin/treatments/{treatment_id} - 없는 리소스는 404
    """
    res = gateway_client.get("/api/v1/admin/treatments/999999")
    assert res.status_code == 404, res.text


def test_admin_update_treatment_success(gateway_client):
    """
    [정상] PUT /api/v1/admin/treatments/{treatment_id}
    """
    created = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 30,
            "price": 10000,
            "description": "",
        },
    )
    assert created.status_code in (200, 201), created.text
    treatment_id = created.json()["id"]

    res = gateway_client.put(
        f"/api/v1/admin/treatments/{treatment_id}",
        json={"price": 15000, "duration_minutes": 60},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["price"] == 15000
    assert body["duration_minutes"] == 60


def test_admin_update_treatment_invalid_duration_400(gateway_client):
    """
    [예외] PUT /api/v1/admin/treatments/{treatment_id}
    - 45분은 '30분 단위' 서비스 검증에 걸려 400
    """
    created = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 30,
            "price": 10000,
            "description": "",
        },
    )
    assert created.status_code in (200, 201), created.text
    treatment_id = created.json()["id"]

    res = gateway_client.put(
        f"/api/v1/admin/treatments/{treatment_id}",
        json={"duration_minutes": 45},
    )
    assert res.status_code == 400, res.text


def test_admin_delete_treatment_success_204(gateway_client):
    """
    [정상] DELETE /api/v1/admin/treatments/{treatment_id} -> 204
    """
    created = gateway_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": f"치료-{uuid4().hex[:6]}",
            "duration_minutes": 30,
            "price": 10000,
            "description": "",
        },
    )
    assert created.status_code in (200, 201), created.text
    treatment_id = created.json()["id"]

    res = gateway_client.delete(f"/api/v1/admin/treatments/{treatment_id}")
    assert res.status_code == 204, res.text

    get_res = gateway_client.get(f"/api/v1/admin/treatments/{treatment_id}")
    assert get_res.status_code == 404, get_res.text


def test_admin_delete_treatment_not_found_404(gateway_client):
    """
    [예외] DELETE /api/v1/admin/treatments/{treatment_id} - 없는 리소스는 404
    """
    res = gateway_client.delete("/api/v1/admin/treatments/999999")
    assert res.status_code == 404, res.text


# =========================================================
# Admin Hospital Slots CRUD
# Base: /api/v1/admin/hospital-slots
# NOTE: request schema uses aliases: start_time/end_time/max_capacity
# =========================================================

def test_admin_create_hospital_slot_success(gateway_client):
    """
    [정상] POST /api/v1/admin/hospital-slots
    - 병원 시간대별 최대 인원 정책 생성 성공
    - 주의: 요청 바디는 alias(start_time/end_time/max_capacity) 사용
    """
    res = gateway_client.post(
        "/api/v1/admin/hospital-slots",
        json={"start_time": "09:00:00", "end_time": "09:30:00", "max_capacity": 3},
    )
    assert res.status_code in (200, 201), res.text
    body = res.json()
    assert body.get("max_capacity", body.get("max_capacity")) == 3


def test_admin_create_hospital_slot_duplicate_409(gateway_client):
    """
    [예외] POST /api/v1/admin/hospital-slots
    - 동일 시간대 슬롯 중복 생성은 409
    """
    first = gateway_client.post(
        "/api/v1/admin/hospital-slots",
        json={"start_time": "10:00:00", "end_time": "10:30:00", "max_capacity": 2},
    )
    assert first.status_code in (200, 201), first.text

    second = gateway_client.post(
        "/api/v1/admin/hospital-slots",
        json={"start_time": "10:00:00", "end_time": "10:30:00", "max_capacity": 2},
    )
    assert second.status_code == 409, second.text


def test_admin_list_hospital_slots_success(gateway_client):
    """
    [정상] GET /api/v1/admin/hospital-slots
    """
    res = gateway_client.get("/api/v1/admin/hospital-slots")
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


def test_admin_list_hospital_slots_method_not_allowed_405(gateway_client):
    """
    [예외] GET 엔드포인트에 PATCH -> 405
    """
    res = gateway_client.patch("/api/v1/admin/hospital-slots")
    assert res.status_code == 405, res.text


def test_admin_update_hospital_slot_success(gateway_client):
    """
    [정상] PUT /api/v1/admin/hospital-slots/{slot_id}
    - max_capacity 변경이 정상 반영되는지 확인
    """
    created = gateway_client.post(
        "/api/v1/admin/hospital-slots",
        json={"start_time": "11:00:00", "end_time": "11:30:00", "max_capacity": 1},
    )
    assert created.status_code in (200, 201), created.text
    slot_id = created.json()["id"]

    res = gateway_client.put(
        f"/api/v1/admin/hospital-slots/{slot_id}",
        json={"max_capacity": 4},
    )
    assert res.status_code == 200, res.text
    assert res.json().get("max_capacity", res.json().get("max_capacity")) == 4


def test_admin_update_hospital_slot_not_found_404(gateway_client):
    """
    [예외] PUT /api/v1/admin/hospital-slots/{slot_id} - 없는 슬롯은 404
    """
    res = gateway_client.put(
        "/api/v1/admin/hospital-slots/999999",
        json={"max_capacity": 2},
    )
    assert res.status_code == 404, res.text


def test_admin_delete_hospital_slot_success_204(gateway_client):
    """
    [정상] DELETE /api/v1/admin/hospital-slots/{slot_id} -> 204
    """
    created = gateway_client.post(
        "/api/v1/admin/hospital-slots",
        json={"start_time": "14:00:00", "end_time": "14:30:00", "max_capacity": 2},
    )
    assert created.status_code in (200, 201), created.text
    slot_id = created.json()["id"]

    res = gateway_client.delete(f"/api/v1/admin/hospital-slots/{slot_id}")
    assert res.status_code == 204, res.text


def test_admin_delete_hospital_slot_not_found_404(gateway_client):
    """
    [예외] DELETE /api/v1/admin/hospital-slots/{slot_id} - 없는 슬롯은 404
    """
    res = gateway_client.delete("/api/v1/admin/hospital-slots/999999")
    assert res.status_code == 404, res.text


# =========================================================
# Admin Appointments
# Base: /api/v1/admin/appointments
# =========================================================

def test_admin_list_appointments_success(gateway_client):
    """
    [정상] GET /api/v1/admin/appointments
    - 데이터가 없어도 200 + list 반환
    """
    res = gateway_client.get("/api/v1/admin/appointments")
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)


def test_admin_list_appointments_invalid_status_filter_400(gateway_client):
    """
    [예외] GET /api/v1/admin/appointments?status=...
    - 유효하지 않은 status는 400
    """
    res = gateway_client.get("/api/v1/admin/appointments", params={"status": "not-a-status"})
    assert res.status_code == 400, res.text


def test_admin_update_appointment_status_success_pending_to_confirmed(gateway_client, seed_master, auth_header):
    """
    [정상] PATCH /api/v1/admin/appointments/{id}/status
    - pending -> confirmed 전이 성공
    """
    doctor_id = seed_master["doctor"].id
    treatment_id = seed_master["treatment"].id
    start_dt = (datetime.now() + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)

    created = gateway_client.post(
        "/api/v1/patient/appointments",
        headers=auth_header,
        json={
            "patient_name": "김철수",
            "patient_phone": "010-3333-4444",
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "start_datetime": start_dt.isoformat(),
            "memo": "관리자 상태 변경 테스트",
        },
    )
    assert created.status_code in (200, 201), created.text
    appt_id = created.json()["id"]

    res = gateway_client.patch(
        f"/api/v1/admin/appointments/{appt_id}/status",
        json={"status": "confirmed"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "confirmed"


def test_admin_update_appointment_status_invalid_transition_400(gateway_client, seed_master, auth_header):
    """
    [예외] PATCH /api/v1/admin/appointments/{id}/status
    - pending -> completed 는 허용되지 않는 전이(중간 confirmed 필요) -> 400
    """
    doctor_id = seed_master["doctor"].id
    treatment_id = seed_master["treatment"].id
    start_dt = (datetime.now() + timedelta(days=1)).replace(hour=16, minute=0, second=0, microsecond=0)

    created = gateway_client.post(
        "/api/v1/patient/appointments",
        headers=auth_header,
        json={
            "patient_name": "김철수",
            "patient_phone": "010-3333-4444",
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "start_datetime": start_dt.isoformat(),
            "memo": "잘못된 전이 테스트",
        },
    )
    assert created.status_code in (200, 201), created.text
    appt_id = created.json()["id"]

    res = gateway_client.patch(
        f"/api/v1/admin/appointments/{appt_id}/status",
        json={"status": "completed"},
    )
    assert res.status_code == 400, res.text


# =========================================================
# Admin Stats
# Base: /api/v1/admin/stats
# =========================================================

def test_admin_stats_success_shape(gateway_client):
    """
    [정상] GET /api/v1/admin/stats
    - 데이터가 비어도 response shape 유지
    """
    res = gateway_client.get("/api/v1/admin/stats")
    assert res.status_code == 200, res.text
    body = res.json()
    expected_keys = {"status_counts", "daily_counts", "time_slot_counts", "visit_type_ratio"}
    assert expected_keys.issubset(set(body.keys())), body


def test_admin_stats_method_not_allowed_405(gateway_client):
    """
    [예외] GET 전용 엔드포인트에 POST -> 405
    """
    res = gateway_client.post("/api/v1/admin/stats")
    assert res.status_code == 405, res.text
