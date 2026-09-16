"""Toscana Sanità Constants."""

import logging

from homeassistant.const import Platform

DOMAIN = "toscana_sanita"
LOGGER = logging.getLogger(__package__)

PLATFORMS = [
    Platform.CALENDAR,
]

CONF_CF = "cf"
CONF_NRE = "nre"
CONF_TEAM = "team"
CONF_PHONE = "phone"
CONF_SERVICE = "service"
CONF_DATA = "data"

STEP_USER = "user"
STEP_ZEROCODE = "zerocode"
STEP_CUP_ONLINE = "cup_online"

EVENT_NEW_CALENDAR_EVENT = f"{DOMAIN}_new_calendar_event"

DEFAULT_REFRESH_INTERVAL = 60  # minutes
