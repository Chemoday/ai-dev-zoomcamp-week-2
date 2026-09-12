from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

# Operating hours per product-spec.md section 3.2: 10:00-22:00.
CLOSING_HOUR = 22


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

    @model_validator(mode="after")
    def _within_operating_hours(self):
        if self.start_time + self.duration > CLOSING_HOUR:
            raise ValueError(
                f"Reservation must end by {CLOSING_HOUR}:00 (start_time + duration exceeds closing)."
            )
        return self


class Reservation(ReservationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @computed_field
    @property
    def end_time(self) -> int:
        return self.start_time + self.duration


class SuccessResult(BaseModel):
    success: bool
