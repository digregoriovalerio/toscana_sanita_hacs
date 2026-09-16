from datetime import datetime

from pydantic import Field

from .availability import QueueRemoteItem
from .calendar import AvailableDay
from .common import CamelCaseModel


class ServiceInfo(CamelCaseModel):
    keyname: str
    enterprise: str
    sys_id: str
    name_service: str
    days: list[AvailableDay]


class ListaDisponibilita(CamelCaseModel):
    day: datetime
    time_delay: str = Field(alias="timeDelay")


class LockResponse(CamelCaseModel):
    expire_on: datetime = Field(alias="expireOn")
    queue_id: str = Field(alias="queueId")
    queue_remote: list[QueueRemoteItem] = Field(alias="queueRemote")
    service: ServiceInfo
    lista_disponibilita: ListaDisponibilita = Field(alias="listaDisponibilita")
    time: int
