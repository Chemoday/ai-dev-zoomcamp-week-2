def test_list_tables_returns_seeded_tables(client):
    resp = client.get("/api/tables")
    assert resp.status_code == 200
    tables = resp.json()
    assert len(tables) == 9
    assert {t["table_number"] for t in tables} == set(range(1, 10))


def test_create_table_succeeds_on_empty_cell(client):
    resp = client.post(
        "/api/tables",
        json={
            "table_number": 42,
            "capacity": 2,
            "table_type": "ROUND_2",
            "grid_x": 5,
            "grid_y": 5,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["table_number"] == 42
    assert body["grid_x"] == 5 and body["grid_y"] == 5


def test_create_table_conflicts_on_duplicate_number(client):
    resp = client.post(
        "/api/tables",
        json={
            "table_number": 1,
            "capacity": 2,
            "table_type": "ROUND_2",
            "grid_x": 5,
            "grid_y": 5,
        },
    )
    assert resp.status_code == 409


def test_create_table_conflicts_on_occupied_coordinate(client):
    resp = client.post(
        "/api/tables",
        json={
            "table_number": 42,
            "capacity": 2,
            "table_type": "ROUND_2",
            "grid_x": 0,
            "grid_y": 0,
        },
    )
    assert resp.status_code == 409


def test_delete_table_without_bookings_succeeds(client):
    tables = client.get("/api/tables").json()
    table_without_bookings = next(t for t in tables if t["table_number"] == 1)

    resp = client.delete(f"/api/tables/{table_without_bookings['id']}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    remaining = client.get("/api/tables").json()
    assert table_without_bookings["id"] not in {t["id"] for t in remaining}


def test_delete_table_with_active_booking_is_blocked(client):
    tables = client.get("/api/tables").json()
    table_with_booking = next(t for t in tables if t["table_number"] == 2)

    resp = client.delete(f"/api/tables/{table_with_booking['id']}")
    assert resp.status_code == 400


def test_delete_nonexistent_table_is_not_found(client):
    resp = client.delete("/api/tables/9999")
    assert resp.status_code == 404
