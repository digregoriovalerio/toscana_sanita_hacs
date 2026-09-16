"""Toscana Sanità integration for Home Assistant."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.components.calendar import CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    CONF_CF,
    CONF_DATA,
    CONF_NRE,
    CONF_PHONE,
    CONF_SERVICE,
    CONF_TEAM,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    EVENT_NEW_CALENDAR_EVENT,
    LOGGER,
    PLATFORMS,
    STEP_CUP_ONLINE,
    STEP_ZEROCODE,
)
from .cup.commands import cerca_appuntamenti
from .zerocode.client import ZeroCodeClient
from .zerocode.commands import SearchFilters, search
from .zerocode.data.search import SearchRequest


@dataclass
class Entry:
    uid: str
    name: str
    address: str
    start_time: datetime
    end_time: datetime
    notes: str = ""

    @staticmethod
    def from_cup_online_data(data: dict[str, Any]) -> "Entry":
        place = data["unita"]["sede"]
        start_time = datetime.strptime(
            f'{data["dataAppuntamento"]} {data["oraAppuntamento"]}',
            "%Y%m%d %H:%M",
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))
        return Entry(
            uid = f"{place['idSede']} {start_time}",
            name = place["descSede"],
            address = f'{place["indirizzoSede"]} - {place["capSede"]}, {place["nomeComuneSede"]} ({place["provinciaSede"]})',
            start_time = start_time,
            end_time = start_time + timedelta(minutes=data["durata"]),
            notes = "\n".join(f"[{s['codiceNomenclatoreRegionale']}] {s['descrizioneNomenclatoreRegionale']}" for s in data.get("listaPrestazioni", []).get("prestazione", []))
        )

    @staticmethod
    def from_zerocode_data(data: dict[str, Any]) -> "Entry":
        start_time = datetime.strptime(
            f'{data["availability"]["day"]} {data["queue_remote_item"]["time"]}',
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))
        return Entry(
            uid = f"{data['enterprise']['sys_id']} {start_time}",
            name = data["enterprise"]["title_enterprise"],
            address = f'{data["enterprise"]["address"]} - {data["enterprise"]["provincia"]}, {data["enterprise"]["regione"]}',
            start_time = start_time,
            end_time = start_time + timedelta(minutes=30)
        )

    @staticmethod
    def from_data(data: dict[str, Any]) -> "Entry":
        service = data[CONF_SERVICE]
        if service == STEP_CUP_ONLINE:
            return Entry.from_cup_online_data(data[CONF_DATA])
        elif service == STEP_ZEROCODE:
            LOGGER.error(f"data = {data}")
            return Entry.from_zerocode_data(data[CONF_DATA])
        else:
            raise ValueError(service)

    def to_calendar_event(self) -> CalendarEvent:
        return CalendarEvent(
            summary=f"{self.name} {self.address}",
            start=self.start_time,
            end=self.end_time,
            location=self.address,
            description=self.notes,
            uid=self.uid,
        )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up Toscana Sanità API from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry with Codice Fiscale, NRE and TEAM number.

    Returns:
        True if setup was successful, False otherwise.
    """
    LOGGER.debug("Setup entry started")

    service = entry.data[CONF_SERVICE]
    cf = entry.data[CONF_CF]
    nre = entry.data[CONF_NRE]
    team = entry.data.get(CONF_TEAM, "")
    phone = entry.data.get(CONF_PHONE, "")

    async def async_fetch_data():

        if service == STEP_ZEROCODE:

            def _fetch_zerocode():
                request = SearchRequest(tax_code=cf, nre=nre, phone_number=phone)
                filters = SearchFilters()
                with ZeroCodeClient() as client:
                    return [Entry.from_data({
                        CONF_DATA: {
                            "enterprise": e.model_dump(),
                            "availability": a.model_dump(),
                            "queue_remote_item": i.model_dump(),
                        },
                        CONF_SERVICE: service
                    }).to_calendar_event() for e, a, i in search(client, request, filters)]

            results = await hass.async_add_executor_job(_fetch_zerocode)

        elif service == STEP_CUP_ONLINE:

            def _fetch_cup_online():
                return [Entry.from_data({
                    CONF_DATA: a.model_dump(),
                    CONF_SERVICE: service
                }).to_calendar_event() for a in cerca_appuntamenti(cf, nre, team)]

            results = await hass.async_add_executor_job(_fetch_cup_online)

        else:
            LOGGER.error(f"Unknown value: {service}")
            raise ValueError(service)

        LOGGER.error(f"Results: {results}")

        old_ids = set()
        if coordinator.data is not None:
            old_ids = {event.uid for event in coordinator.data}

        new_ids = {event.uid for event in results}
        LOGGER.error(f"Old events: {old_ids}")
        LOGGER.error(f"New events: {new_ids}")

        if new_ids - old_ids:
            LOGGER.error("Notifying new events!")
            hass.bus.async_fire(
                EVENT_NEW_CALENDAR_EVENT,
                {
                    "nre": nre,
                },
            )

        LOGGER.debug(f"Found {len(results)} for {nre}")
        return results

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=nre,
        update_method=async_fetch_data,
        update_interval=timedelta(minutes=DEFAULT_REFRESH_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    LOGGER.debug("Setup entry terminated successfully")
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload a config entry and clean up resources.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry to unload.

    Returns:
        True if unload was successful, False otherwise.
    """
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if result:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    LOGGER.debug(
        f"Unload entry {'terminated successfully' if result else 'has failed'}"
    )
    return result
