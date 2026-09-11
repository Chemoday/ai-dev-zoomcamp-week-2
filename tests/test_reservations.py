from datetime import date


def today():
    return date.today().isoformat()


def test_list_reservations_for_seeded_date(client):
    resp = client.get("/api/reservations", params={"date": today()})
    assert resp.status_code == 200
    reservations = resp.json()
    assert len(reservations) == 4
    # sorted by start_time
    assert [r["start_time"] for r in reservations] == sorted(r["start_time"] for r in reservations)


def test_create_reservation_on_free_table_succeeds(client):
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    table_id = tables[1]["id"]  # table 1 has no seeded bookings

    resp = client.post(
        "/api/reservations",
        json={
            "table_id": table_id,
            "customer_name": "Test Guest",
            "customer_phone": "555-0000",
            "reservation_date": today(),
            "start_time": 15,
            "duration": 2,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["table_id"] == table_id
    assert body["end_time"] == 17


def test_create_reservation_conflicts_on_overlap(client):
    # seeded booking: table_number 2, start_time 18, duration 3 (18-21)
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    table_id = tables[2]["id"]

    resp = client.post(
        "/api/reservations",
        json={
            "table_id": table_id,
            "customer_name": "Conflict Guest",
            "customer_phone": "555-1111",
            "reservation_date": today(),
            "start_time": 19,
            "duration": 1,
        },
    )
    assert resp.status_code == 409


def test_create_reservation_for_unknown_table_is_not_found(client):
    resp = client.post(
        "/api/reservations",
        json={
            "table_id": 9999,
            "customer_name": "Ghost Guest",
            "customer_phone": "555-2222",
            "reservation_date": today(),
            "start_time": 15,
            "duration": 1,
        },
    )
    assert resp.status_code == 404


def test_cancel_reservation_succeeds_then_frees_the_table(client):
    reservations = client.get("/api/reservations", params={"date": today()}).json()
    reservation = reservations[0]

    resp = client.delete(f"/api/reservations/{reservation['id']}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    remaining = client.get("/api/reservations", params={"date": today()}).json()
    assert reservation["id"] not in {r["id"] for r in remaining}


def test_cancel_nonexistent_reservation_is_not_found(client):
    resp = client.delete("/api/reservations/9999")
    assert resp.status_code == 404
