"""Exercises the exact overlap boundary from product-spec.md section 3.3:

    A table is unavailable if NOT (E_new <= S_res OR S_new >= E_res)

i.e. touching windows (one starts exactly when the other ends) must NOT
count as a conflict, but any actual overlap must.
"""

from datetime import date, timedelta


def today():
    return date.today().isoformat()


def book(client, table_id, start_time, duration, name="Guest"):
    return client.post(
        "/api/reservations",
        json={
            "table_id": table_id,
            "customer_name": name,
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": start_time,
            "duration": duration,
        },
    )


def free_table_id(client, table_number=1):
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    return tables[table_number]["id"]


def test_back_to_back_booking_right_after_existing_is_not_a_conflict(client):
    table_id = free_table_id(client)
    first = book(client, table_id, 10, 2, "First")  # 10-12
    assert first.status_code == 201

    second = book(client, table_id, 12, 2, "Second")  # 12-14, starts exactly when first ends
    assert second.status_code == 201


def test_back_to_back_booking_right_before_existing_is_not_a_conflict(client):
    table_id = free_table_id(client)
    first = book(client, table_id, 12, 2, "First")  # 12-14
    assert first.status_code == 201

    second = book(client, table_id, 10, 2, "Second")  # 10-12, ends exactly when first starts
    assert second.status_code == 201


def test_overlap_by_one_hour_is_a_conflict(client):
    table_id = free_table_id(client)
    first = book(client, table_id, 10, 2, "First")  # 10-12
    assert first.status_code == 201

    second = book(client, table_id, 11, 2, "Second")  # 11-13, overlaps 11-12
    assert second.status_code == 409


def test_fully_nested_booking_is_a_conflict(client):
    table_id = free_table_id(client)
    first = book(client, table_id, 10, 4, "First")  # 10-14
    assert first.status_code == 201

    second = book(client, table_id, 11, 1, "Second")  # 11-12, inside 10-14
    assert second.status_code == 409


def test_identical_window_is_a_conflict(client):
    table_id = free_table_id(client)
    first = book(client, table_id, 15, 2, "First")
    assert first.status_code == 201

    second = book(client, table_id, 15, 2, "Second")
    assert second.status_code == 409


def test_different_tables_never_conflict(client):
    table_a = free_table_id(client, table_number=1)
    table_b = free_table_id(client, table_number=4)

    first = book(client, table_a, 15, 2, "First")
    second = book(client, table_b, 15, 2, "Second")
    assert first.status_code == 201
    assert second.status_code == 201


def test_same_window_different_date_never_conflicts(client):
    table_id = free_table_id(client)
    first = client.post(
        "/api/reservations",
        json={
            "table_id": table_id,
            "customer_name": "Today",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 15,
            "duration": 2,
        },
    )
    assert first.status_code == 201

    tomorrow = (date.fromisoformat(today()) + timedelta(days=1)).isoformat()

    second = client.post(
        "/api/reservations",
        json={
            "table_id": table_id,
            "customer_name": "Tomorrow",
            "customer_phone": "555-0000",
            "reservation_date": tomorrow,
            "start_time": 15,
            "duration": 2,
        },
    )
    assert second.status_code == 201
