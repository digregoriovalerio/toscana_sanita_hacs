"""Config flow for the Toscana Sanità integration."""
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_CF,
    CONF_NRE,
    CONF_PHONE,
    CONF_SERVICE,
    CONF_TEAM,
    DOMAIN,
    LOGGER,
    STEP_CUP_ONLINE,
    STEP_USER,
    STEP_ZEROCODE,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVICE, default=STEP_ZEROCODE): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(
                        value=STEP_ZEROCODE, label="ZeroCode"
                    ),
                    SelectOptionDict(
                        value=STEP_CUP_ONLINE, label="CUP Online"
                    ),
                ],
                mode=SelectSelectorMode.LIST,
            )
        ),
    }
)

# TODO handle filter
STEP_ZEROCODE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CF): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_NRE): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_PHONE): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEL)
        ),
    }
)

# TODO handle filter
STEP_CUP_ONLINE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CF): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_NRE): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)  # TODO must be a list
        ),
        vol.Required(CONF_TEAM): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
    }
)


class ToscanaSanitaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Toscana Sanità integration.

    This flow manages user configuration and validation for connecting
    to the CUP Online service using Codice Fiscale, NRE and TEAM number.
    """

    VERSION = 1
    def __init__(self) -> None:
        """Initialize flow state to hold data across steps."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user setup step.

        This step prompts the user for choosing between ZeroCode or CUP Online services.

        Args:
            user_input: Dictionary containing the choice from the form.

        Returns:
            A config flow result with either the entry creation or the form.
        """
        errors: dict[str, str] = {}

        LOGGER.debug("Step user started")
        if user_input is not None:
            self._data.update(user_input)
            LOGGER.debug(f"Step {STEP_USER} choice: {user_input[CONF_SERVICE]}")
            if user_input[CONF_SERVICE] == STEP_ZEROCODE:
                return await self.async_step_zerocode()
            elif user_input[CONF_SERVICE] == STEP_CUP_ONLINE:
                return await self.async_step_cup_online()
            else:
                LOGGER.error(f"Unknown value: {user_input[CONF_SERVICE]}")
                raise ValueError(user_input[CONF_SERVICE])
        LOGGER.debug(f"Step {STEP_USER} terminated with form")
        return self.async_show_form(
            step_id=STEP_USER,
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )


    async def async_step_zerocode(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user setup step.

        This step prompts the user for their Codice Fiscale, NRE and telephone number,
        then creates a config entry.

        Args:
            user_input: Dictionary containing Codice Fiscale, NRE and telephone number from the form.

        Returns:
            A config flow result with either the entry creation or the form.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(user_input[CONF_NRE])
            self._abort_if_unique_id_configured()
            result = self.async_create_entry(title=user_input[CONF_NRE], data=self._data)
            LOGGER.debug(f"Step {STEP_ZEROCODE} for '{user_input[CONF_NRE]}' terminated")
            return result

        result = self.async_show_form(
            step_id=STEP_ZEROCODE,
            data_schema=STEP_ZEROCODE_DATA_SCHEMA,
            errors=errors,
        )

        LOGGER.debug(f"Step {STEP_ZEROCODE} terminated with form")
        return result

    async def async_step_cup_online(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user setup step.

        This step prompts the user for their Codice Fiscale, NRE and TEAM number,
        then creates a config entry.

        Args:
            user_input: Dictionary containing Codice Fiscale, NRE and TEAM number from the form.

        Returns:
            A config flow result with either the entry creation or the form.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(user_input[CONF_NRE])
            self._abort_if_unique_id_configured()
            result = self.async_create_entry(title=user_input[CONF_NRE], data=self._data)
            LOGGER.debug(f"Step {STEP_CUP_ONLINE} for '{user_input[CONF_NRE]}' terminated")
            return result

        result = self.async_show_form(
            step_id=STEP_CUP_ONLINE,
            data_schema=STEP_CUP_ONLINE_DATA_SCHEMA,
            errors=errors,
        )

        LOGGER.debug(f"Step {STEP_CUP_ONLINE} terminated with form")
        return result