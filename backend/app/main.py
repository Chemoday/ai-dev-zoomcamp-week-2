from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, SessionLocal, engine, get_db

# Mirrors frontend/src/services/api.js's seed() exactly, so Phase 3
# integration (flipping USE_MOCKS = false) shows the same floor plan
# the frontend was built and demoed against. Deviates from
# product-spec.md section 7.1 (which lists 5 tables with string
# table_numbers like "T-1") because openapi.yaml already settled on
# integer table_number to match the frontend's actual behavior.
SEED_TABLES = [
    {"table_number": 1, "capacity": 2, "table_type": "ROUND_2", "grid_x": 0, "grid_y": 0},
    {"table_number": 2, "capacity": 2, "table_type": "ROUND_2", "grid_x": 2, "grid_y": 0},
    {"table_number": 3, "capacity": 4, "table_type": "RECT_4", "grid_x": 4, "grid_y": 0},
    {"table_number": 4, "capacity": 4, "table_type": "RECT_4", "grid_x": 1, "grid_y": 2},
    {"table_number": 5, "capacity": 6, "table_type": "LONG_6", "grid_x": 3, "grid_y": 2},
    {"table_number": 6, "capacity": 2, "table_type": "ROUND_2", "grid_x": 5, "grid_y": 2},
    {"table_number": 7, "capacity": 4, "table_type": "RECT_4", "grid_x": 0, "grid_y": 4},
    {"table_number": 8, "capacity": 6, "table_type": "LONG_6", "grid_x": 2, "grid_y": 4},
    {"table_number": 9, "capacity": 4, "table_type": "RECT_4", "grid_x": 4, "grid_y": 5},
]


def seed_if_empty(db: Session) -> None:
    if db.query(models.Table).count() > 0:
        return

    tables = [models.Table(**data) for data in SEED_TABLES]
    db.add_all(tables)
    db.commit()
    for table in tables:
        db.refresh(table)

    today = date.today()
    by_number = {t.table_number: t.id for t in tables}
    seed_reservations = [
        {"table_id": by_number[2], "customer_name": "Marguerite Hale", "customer_phone": "(555) 014 8820", "reservation_date": today, "start_time": 18, "duration": 3},
        {"table_id": by_number[5], "customer_name": "Ivo Brandt", "customer_phone": "(555) 902 1177", "reservation_date": today, "start_time": 19, "duration": 3},
        {"table_id": by_number[7], "customer_name": "Dala Okonkwo", "customer_phone": "(555) 771 3390", "reservation_date": today, "start_time": 21, "duration": 2},
        {"table_id": by_number[3], "customer_name": "Petra Lindqvist", "customer_phone": "(555) 336 0042", "reservation_date": today, "start_time": 12, "duration": 2},
    ]
    db.add_all(models.Reservation(**data) for data in seed_reservations)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No Alembic per product-spec.md section 7.1 — create_all + a
    # one-time seed is enough for this module.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Interactive Restaurant Table Reservation System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tables", response_model=list[schemas.Table])
def list_tables(db: Session = Depends(get_db)):
    return crud.get_tables(db)


@app.post("/api/tables", response_model=schemas.Table, status_code=201)
def create_table(table_in: schemas.TableCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_table(db, table_in)
    except crud.ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.delete("/api/tables/{table_id}", response_model=schemas.DeleteTableResult)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    if crud.get_table(db, table_id) is None:
        raise HTTPException(status_code=404, detail="Table not found.")
    try:
        crud.delete_table(db, table_id, today=date.today())
    except crud.BlockedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return schemas.DeleteTableResult(success=True, message="Table deleted successfully")


@app.get("/api/availability", response_model=list[schemas.AvailabilityEntry])
def get_availability(
    date: date = Query(...),
    start_time: int = Query(..., ge=10, le=21),
    duration: int = Query(..., ge=1, le=4),
    party_size: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return crud.get_availability(db, date, start_time, duration, party_size)


@app.get("/api/reservations", response_model=list[schemas.Reservation])
def list_reservations(date: date | None = Query(default=None), db: Session = Depends(get_db)):
    return crud.get_reservations(db, date)


@app.post("/api/reservations", response_model=schemas.Reservation, status_code=201)
def create_reservation(res_in: schemas.ReservationCreate, db: Session = Depends(get_db)):
    if crud.get_table(db, res_in.table_id) is None:
        raise HTTPException(status_code=404, detail="Table not found.")
    try:
        return crud.create_reservation(db, res_in)
    except crud.ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.delete("/api/reservations/{reservation_id}", response_model=schemas.SuccessResult)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    if not crud.delete_reservation(db, reservation_id):
        raise HTTPException(status_code=404, detail="Reservation not found.")
    return schemas.SuccessResult(success=True)
