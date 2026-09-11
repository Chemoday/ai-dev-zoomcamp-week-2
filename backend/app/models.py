from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    table_type: Mapped[str] = mapped_column(String, nullable=False)
    grid_x: Mapped[int] = mapped_column(Integer, nullable=False)
    grid_y: Mapped[int] = mapped_column(Integer, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    reservation_date: Mapped[str] = mapped_column(Date, nullable=False)
    start_time: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
