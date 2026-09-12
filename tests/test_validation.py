"""Request-validation edge cases (422s) not covered by the happy/blocked
path tests in test_tables.py / test_reservations.py.
"""

from datetime import date


def today():
    return date.today().isoformat()


# --- Tables --------------------------------------------------------------


def test_create_table_rejects_unknown_table_type(client):
    resp = client.post(
        "/api/tables",
        json={"table_number": 50, "capacity": 4, "table_type": "SQUARE_8", "grid_x": 5, "grid_y": 5},
    )
    assert resp.status_code == 422


def test_create_table_rejects_grid_x_out_of_range(client):
    resp = client.post(
        "/api/tables",
        json={"table_number": 50, "capacity": 2, "table_type": "ROUND_2", "grid_x": 6, "grid_y": 0},
    )
    assert resp.status_code == 422


def test_create_table_rejects_negative_grid_y(client):
    resp = client.post(
        "/api/tables",
        json={"table_number": 50, "capacity": 2, "table_type": "ROUND_2", "grid_x": 0, "grid_y": -1},
    )
    assert resp.status_code == 422


def test_create_table_rejects_missing_fields(client):
    resp = client.post("/api/tables", json={"table_number": 50})
    assert resp.status_code == 422


# --- Reservations ----------------------------------------------------------


def test_create_reservation_rejects_start_time_before_opening(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "Early Bird",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 9,
            "duration": 1,
        },
    )
    assert resp.status_code == 422


def test_create_reservation_rejects_duration_over_max(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "Long Stay",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 10,
            "duration": 5,
        },
    )
    assert resp.status_code == 422


def test_create_reservation_rejects_window_past_closing(client):
    # start_time=21 is individually valid (<=21) and duration=2 is
    # individually valid (<=4), but 21 + 2 = 23 is past the 22:00 close.
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "Night Owl",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 21,
            "duration": 2,
        },
    )
    assert resp.status_code == 422


def test_create_reservation_ending_exactly_at_closing_is_allowed(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "Just In Time",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 21,
            "duration": 1,
        },
    )
    assert resp.status_code == 201
    assert resp.json()["end_time"] == 22


def test_create_reservation_rejects_empty_customer_name(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 10,
            "duration": 1,
        },
    )
    assert resp.status_code == 422


def test_create_reservation_rejects_malformed_date(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 1,
            "customer_name": "Bad Date",
            "customer_phone": "555-0000",
            "reservation_date": "20-11-2023",
            "start_time": 10,
            "duration": 1,
        },
    )
    assert resp.status_code == 422


# --- Availability ------------------------------------------------------


def test_availability_requires_party_size(client):
    resp = client.get(
        "/api/availability", params={"date": today(), "start_time": 10, "duration": 1}
    )
    assert resp.status_code == 422


def test_availability_rejects_zero_party_size(client):
    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 10, "duration": 1, "party_size": 0},
    )
    assert resp.status_code == 422


def test_availability_rejects_window_past_closing(client):
    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 21, "duration": 2, "party_size": 2},
    )
    assert resp.status_code == 422


def test_availability_rejects_duration_over_max(client):
    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 10, "duration": 5, "party_size": 2},
    )
    assert resp.status_code == 422
