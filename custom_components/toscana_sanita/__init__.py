"""Toscana Sanità integration for Home Assistant."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .api import Platform
from .const import (
    CONF_CF,
    CONF_NRE,
    CONF_PHONE,
    CONF_SERVICE,
    CONF_TEAM,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    EVENT_NEW_CALENDAR_EVENT,
    LOGGER,
    PLATFORMS,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
        platform = Platform.get(service)

        def fetch():
            return list(platform.search(cf, nre, team=team, phone=phone))

        results = await hass.async_add_executor_job(fetch)
        LOGGER.debug(f"Results: {results}")

        old_ids = set()
        if coordinator.data is not None:
            old_ids = {event.uid for event in coordinator.data}

        new_ids = {event.uid for event in results}
        LOGGER.debug(f"Old events: {old_ids}")
        LOGGER.debug(f"New events: {new_ids}")

        if new_ids - old_ids:
            LOGGER.debug("Notifying new events!")
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


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
