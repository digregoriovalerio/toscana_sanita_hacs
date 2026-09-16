"""Toscana Sanità Binary Sensor definitions."""
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_NRE,
    DOMAIN,
    LOGGER,
)


def format_timedelta_hhmm(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return f"{hours:02d}:{minutes:02d}"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up a calendar entities from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry with integration data.
        async_add_entities: Callback to add new entities.
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]
    LOGGER.info(f"Loading calendar {entry.data[CONF_NRE]}.")
    async_add_entities([ToscanaSanitaCalendarEntity(coordinator, entry)])


class ToscanaSanitaCalendarEntity(CoordinatorEntity, CalendarEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = entry.data[CONF_NRE]
        self._attr_unique_id = entry.data[CONF_NRE]
        self.event_uids: set[str] = set()

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self.coordinator.data or []
        now = datetime.now().astimezone()
        future_events = [e for e in events if e.start >= now]
        return min(future_events, key=lambda e: e.start) if future_events else None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        """Return calendar events within datetime range."""
        events = self.coordinator.data or []
        return [
            e for e in events 
            if e.start < end_date and e.end > start_date
        ]
