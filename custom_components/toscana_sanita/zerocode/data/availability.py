from datetime import date

from pydantic import Field

from .common import CamelCaseModel


class AvailabilityRequest(CamelCaseModel):
    day: date
    time_delay: str = Field(alias="timeDelay")


class QueueRemoteItem(CamelCaseModel):
    queue_remote_id: str
    time: str
    key_name: str = Field(alias="keyName")


class AvailabilityResponse(CamelCaseModel):
    queue_remote: list[QueueRemoteItem]
