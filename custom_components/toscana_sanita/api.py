"""Toscana Sanità integration for Home Assistant."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterator, Protocol
from zoneinfo import ZoneInfo

from homeassistant.components.calendar import CalendarEvent

from .const import LOGGER, SERVICE_CUP_ONLINE, SERVICE_ZEROCODE
from .cup.commands import cerca_appuntamenti
from .zerocode.client import ZeroCodeClient
from .zerocode.commands import SearchFilters, search
from .zerocode.data.search import SearchRequest


class Platform(Protocol):
    @staticmethod
    def get(service: str) -> Platform:
        if service == SERVICE_ZEROCODE:
            return Zerocode()
        elif service == SERVICE_CUP_ONLINE:
            return CUPOnline()
        else:
            LOGGER.error(f"Unknown value: {service}")
            raise ValueError(service)

    def validate(self, cf: str, nre: str, **kwargs) -> None:
        list(self.search(cf, nre, **kwargs))

    def search(
        self, cf: str, nre: str, **kwargs
    ) -> Iterator[CalendarEvent]: ...


class Zerocode(Platform):
    @staticmethod
    def data_to_event(data: dict[str, Any]) -> CalendarEvent:
        start_time = datetime.strptime(
            f"{data['availability']['day']} "
            f"{data['queue_remote_item']['time']}",
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))
        name = (data["enterprise"]["title_enterprise"],)
        address = (
            f"{data['enterprise']['address']} - "
            f"{data['enterprise']['provincia']}, "
            f"{data['enterprise']['regione']}"
        )
        return CalendarEvent(
            summary=f"{name} {address}",
            start=start_time,
            end=start_time + timedelta(minutes=30),
            location=address,
            uid=f"{data['enterprise']['sys_id']} {start_time}",
        )

    def search(self, cf: str, nre: str, **kwargs) -> Iterator[CalendarEvent]:
        request = SearchRequest(
            tax_code=cf, nre=nre, phone_number=kwargs["phone"]
        )
        filters = SearchFilters()
        with ZeroCodeClient() as client:
            for e, a, i in search(client, request, filters):
                yield self.data_to_event(
                    {
                        "enterprise": e.model_dump(),
                        "availability": a.model_dump(),
                        "queue_remote_item": i.model_dump(),
                    }
                )


class CUPOnline(Platform):
    @staticmethod
    def data_to_event(data: dict[str, Any]) -> CalendarEvent:
        place = data["unita"]["sede"]
        start_time = datetime.strptime(
            f"{data['dataAppuntamento']} {data['oraAppuntamento']}",
            "%Y%m%d %H:%M",
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))
        address = (
            f"{place['indirizzoSede']} - {place['capSede']}, "
            f"{place['nomeComuneSede']} ({place['provinciaSede']})"
        )
        return CalendarEvent(
            summary=f"{place['descSede']} {address}",
            start=start_time,
            end=start_time + timedelta(minutes=data["durata"]),
            location=address,
            description="\n".join(
                (
                    f"[{s['codiceNomenclatoreRegionale']}] "
                    f"{s['descrizioneNomenclatoreRegionale']}"
                )
                for s in data.get("listaPrestazioni", []).get("prestazione", [])
            ),
            uid=f"{place['idSede']} {start_time}",
        )

    def search(self, cf: str, nre: str, **kwargs) -> Iterator[CalendarEvent]:
        for a in cerca_appuntamenti(cf, nre, kwargs["team"]):
            yield self.data_to_event(a.model_dump())
