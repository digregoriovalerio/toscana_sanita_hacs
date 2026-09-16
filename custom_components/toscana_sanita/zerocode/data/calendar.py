from datetime import date

from pydantic import Field

from .common import CamelCaseModel


class AvailableDay(CamelCaseModel):
    day: date


class CalendarResponse(CamelCaseModel):
    available_days: list[AvailableDay] = Field(alias="availableDays")
    move_reservation_msg: str = Field(alias="moveReservationMsg")
