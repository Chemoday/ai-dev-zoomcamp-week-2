from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field


class TableType(str, Enum):
    ROUND_2 = "ROUND_2"
    RECT_4 = "RECT_4"
    LONG_6 = "LONG_6"


class TableCreate(BaseModel):
    table_number: int
    capacity: int
    table_type: TableType
    grid_x: int = Field(ge=0, le=5)
    grid_y: int = Field(ge=0, le=5)


class Table(TableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DeleteTableResult(BaseModel):
    success: bool
    message: str


class AvailabilityEntry(BaseModel):
    table_id: int
    is_reserved: bool
    fits_party: bool
    is_available: bool


class ReservationCreate(BaseModel):
    table_id: int
    customer_name: str = Field(min_length=1)
    customer_phone: str = Field(min_length=1)
    reservation_date: date
    start_time: int = Field(ge=10, le=21)
    duration: int = Field(ge=1, le=4)


class Reservation(ReservationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @computed_field
    @property
    def end_time(self) -> int:
        return self.start_time + self.duration


class SuccessResult(BaseModel):
    success: bool
