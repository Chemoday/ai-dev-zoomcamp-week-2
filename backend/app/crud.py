from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


class ConflictError(Exception):
    """Raised when a create request collides with existing data (-> 409)."""


class BlockedError(Exception):
    """Raised when a delete is blocked by dependent data (-> 400)."""


def _overlaps(res: models.Reservation, target_date: date, start_time: int, duration: int) -> bool:
    return (
        res.reservation_date == target_date
        and res.start_time < start_time + duration
        and start_time < res.start_time + res.duration
    )


def get_tables(db: Session) -> list[models.Table]:
    return list(db.scalars(select(models.Table)).all())


def get_table(db: Session, table_id: int) -> models.Table | None:
    return db.get(models.Table, table_id)


def create_table(db: Session, table_in: schemas.TableCreate) -> models.Table:
    taken = db.scalars(
        select(models.Table).where(
            (models.Table.table_number == table_in.table_number)
            | (
                (models.Table.grid_x == table_in.grid_x)
                & (models.Table.grid_y == table_in.grid_y)
            )
        )
    ).first()
    if taken:
        raise ConflictError("That table number or position is already taken.")

    table = models.Table(**table_in.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def delete_table(db: Session, table_id: int, today: date) -> None:
    has_bookings = db.scalars(
        select(models.Reservation).where(
            models.Reservation.table_id == table_id,
            models.Reservation.reservation_date >= today,
        )
    ).first()
    if has_bookings:
        raise BlockedError("Cannot delete table with active bookings.")

    table = db.get(models.Table, table_id)
    if table is not None:
        db.delete(table)
        db.commit()


def get_availability(
    db: Session, target_date: date, start_time: int, duration: int, party_size: int
) -> list[schemas.AvailabilityEntry]:
    tables = get_tables(db)
    reservations = list(
        db.scalars(
            select(models.Reservation).where(models.Reservation.reservation_date == target_date)
        ).all()
    )

    entries = []
    for table in tables:
        is_reserved = any(
            r.table_id == table.id and _overlaps(r, target_date, start_time, duration)
            for r in reservations
        )
        fits_party = table.capacity >= party_size
        entries.append(
            schemas.AvailabilityEntry(
                table_id=table.id,
                is_reserved=is_reserved,
                fits_party=fits_party,
                is_available=(not is_reserved) and fits_party,
            )
        )
    return entries


def get_reservations(db: Session, target_date: date | None) -> list[models.Reservation]:
    query = select(models.Reservation)
    if target_date is not None:
        query = query.where(models.Reservation.reservation_date == target_date)
    query = query.order_by(models.Reservation.start_time)
    return list(db.scalars(query).all())


def create_reservation(db: Session, res_in: schemas.ReservationCreate) -> models.Reservation:
    existing = list(
        db.scalars(
            select(models.Reservation).where(
                models.Reservation.table_id == res_in.table_id,
                models.Reservation.reservation_date == res_in.reservation_date,
            )
        ).all()
    )
    conflict = any(
        _overlaps(r, res_in.reservation_date, res_in.start_time, res_in.duration)
        for r in existing
    )
    if conflict:
        raise ConflictError("This table was just booked. Pick another.")

    reservation = models.Reservation(**res_in.model_dump())
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def delete_reservation(db: Session, reservation_id: int) -> bool:
    reservation = db.get(models.Reservation, reservation_id)
    if reservation is None:
        return False
    db.delete(reservation)
    db.commit()
    return True
