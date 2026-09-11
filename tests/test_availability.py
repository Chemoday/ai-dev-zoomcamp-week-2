from datetime import date


def today():
    return date.today().isoformat()


def test_available_table_marked_available_for_free_slot(client):
    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 10, "duration": 1, "party_size": 2},
    )
    assert resp.status_code == 200
    entries = {e["table_id"]: e for e in resp.json()}
    tables = {t["id"]: t for t in client.get("/api/tables").json()}
    table_1_id = next(t["id"] for t in tables.values() if t["table_number"] == 1)
    assert entries[table_1_id]["is_available"] is True
    assert entries[table_1_id]["is_reserved"] is False


def test_reserved_table_marked_unavailable_in_overlapping_window(client):
    # seeded booking: table_number 2, start_time 18, duration 3 (18-21)
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    table_2_id = tables[2]["id"]

    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 19, "duration": 1, "party_size": 2},
    )
    entries = {e["table_id"]: e for e in resp.json()}
    assert entries[table_2_id]["is_reserved"] is True
    assert entries[table_2_id]["is_available"] is False


def test_reserved_table_marked_available_outside_window(client):
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    table_2_id = tables[2]["id"]

    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 10, "duration": 1, "party_size": 2},
    )
    entries = {e["table_id"]: e for e in resp.json()}
    assert entries[table_2_id]["is_reserved"] is False


def test_table_too_small_for_party_is_not_available(client):
    tables = {t["table_number"]: t for t in client.get("/api/tables").json()}
    table_1_id = tables[1]["id"]  # capacity 2

    resp = client.get(
        "/api/availability",
        params={"date": today(), "start_time": 10, "duration": 1, "party_size": 6},
    )
    entries = {e["table_id"]: e for e in resp.json()}
    assert entries[table_1_id]["fits_party"] is False
    assert entries[table_1_id]["is_available"] is False
