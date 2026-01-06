-- Doctor
INSERT INTO doctors (id, name, department)
VALUES
  (1, '김원장', '피부과'),
  (2, '이원장', '성형외과');

-- Treatment
INSERT INTO treatments (id, name, duration_minutes, price, description)
VALUES
  (1, '여드름 치료', 30, 10000, '기본 여드름 치료'),
  (2, '레이저 시술', 60, 50000, '피부 레이저 시술');

-- HospitalSlot (09:00~18:00, 30분 단위 // 점심시간(12~13)은 제외)
INSERT INTO hospital_slots (start_time, end_time, max_capacity) VALUES
('09:00:00', '09:30:00', 2),
('09:30:00', '10:00:00', 2),
('10:00:00', '10:30:00', 2),
('10:30:00', '11:00:00', 2),
('11:00:00', '11:30:00', 2),
('11:30:00', '12:00:00', 2),
('13:00:00', '13:30:00', 2),
('13:30:00', '14:00:00', 2),
('14:00:00', '14:30:00', 2),
('14:30:00', '15:00:00', 2),
('15:00:00', '15:30:00', 2),
('15:30:00', '16:00:00', 2),
('16:00:00', '16:30:00', 2),
('16:30:00', '17:00:00', 2),
('17:00:00', '17:30:00', 2),
('17:30:00', '18:00:00', 2);

-- Patient
INSERT INTO patients (id, name, phone_number)
VALUES
  (1, '홍길동', '010-1111-2222'),
  (2, '김철수', '010-3333-4444');

-- Appointment (모델 기준: status, is_first_visit, memo)
INSERT INTO appointments (
  id,
  patient_id,
  doctor_id,
  treatment_id,
  start_datetime,
  end_datetime,
  status,
  is_first_visit,
  memo
) VALUES
(
  1,
  1,
  1,
  1,
  '2026-01-03 10:15:00',
  '2026-01-03 10:45:00',
  'confirmed',
  'first',
  '샘플 예약'
);
