"""Config flow for the Toscana Sanità integration."""

import asyncio
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import Platform
from .const import (
    CONF_CF,
    CONF_NRE,
    CONF_PHONE,
    CONF_SERVICE,
    CONF_TEAM,
    DOMAIN,
    LOGGER,
    SERVICE_CUP_ONLINE,
    SERVICE_ZEROCODE,
    STEP_INIT,
    STEP_SERVICE,
    STEP_USER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVICE, default=SERVICE_ZEROCODE): SelectSelector(
            SelectSelectorConfig(
                options=[SERVICE_ZEROCODE, SERVICE_CUP_ONLINE],
                mode=SelectSelectorMode.LIST,
                translation_key=CONF_SERVICE,
            )
        ),
    }
)


def get_service_schema(
    service: str, data: dict[str, Any] | None = None
) -> vol.Schema:
    data = data or {}
    if service == SERVICE_ZEROCODE:
        # TODO handle filtering
        return vol.Schema(
            {
                vol.Required(
                    CONF_CF, default=data.get(CONF_CF, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(
                    CONF_NRE, default=data.get(CONF_NRE, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(
                    CONF_PHONE, default=data.get(CONF_PHONE, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEL)),
            }
        )
    elif service == SERVICE_CUP_ONLINE:
        # TODO handle filtering
        # TODO nre must be a list
        return vol.Schema(
            {
                vol.Required(
                    CONF_CF, default=data.get(CONF_CF, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(
                    CONF_NRE, default=data.get(CONF_NRE, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(
                    CONF_TEAM, default=data.get(CONF_TEAM, vol.UNDEFINED)
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
            }
        )
    else:
        LOGGER.error(f"Unknown value: {service}")
        raise ValueError(service)


class ToscanaSanitaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Toscana Sanità integration.

    This flow manages user configuration and validation for connecting
    to the CUP Online service using Codice Fiscale, NRE and TEAM number.
    """

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow state to hold data across steps."""
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return ToscanaSanitaOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user setup step.

        This step prompts the user for choosing between ZeroCode or CUP Online
        services.

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
            if user_input[CONF_SERVICE] in (
                SERVICE_ZEROCODE,
                SERVICE_CUP_ONLINE,
            ):
                return await self.async_step_service()

            LOGGER.error(f"Unknown value: {user_input[CONF_SERVICE]}")
            raise ValueError(user_input[CONF_SERVICE])
        LOGGER.debug(f"Step {STEP_USER} terminated with form")
        return self.async_show_form(
            step_id=STEP_USER, data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_service(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the service setup step.

        This step prompts with a schema, then creates a config entry.

        Args:
            service: the service exposed by the target platform.
            user_input: Dictionary containing data from the form.

        Returns:
            A config flow result with either the entry creation or the form.
        """
        errors: dict[str, str] = {}
        extras: dict[str, str] = {}

        service = self._data.get(CONF_SERVICE)
        if not service:
            LOGGER.error("Unknown service")
            raise ValueError("Unknown service")

        if user_input is not None:
            try:
                platform = Platform.get(service)
                await asyncio.to_thread(
                    platform.validate,
                    user_input[CONF_CF],
                    user_input[CONF_NRE],
                    team=user_input.get(CONF_TEAM),
                    phone=user_input.get(CONF_PHONE),
                )
                self._data.update(user_input)
                await self.async_set_unique_id(user_input[CONF_NRE])
                self._abort_if_unique_id_configured()
                result = self.async_create_entry(
                    title=user_input[CONF_NRE], data=self._data
                )
                LOGGER.debug(
                    f"Step {service} for '{user_input[CONF_NRE]}' terminated"
                )
                return result
            except Exception as e:
                LOGGER.warning(str(e))
                errors["base"] = "invalid_input"
                extras["error_message"] = str(e)

        result = self.async_show_form(
            step_id=STEP_SERVICE,
            data_schema=get_service_schema(service, self._data),
            errors=errors,
            description_placeholders=extras,
        )

        LOGGER.debug(f"Step {service} terminated with form")
        return result


class ToscanaSanitaOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Toscana Sanità integration."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options for the configuration entry."""
        errors: dict[str, str] = {}
        extras: dict[str, str] = {}

        current_data = {**self._config_entry.data, **self._config_entry.options}
        service = current_data.get(CONF_SERVICE)
        if not service:
            LOGGER.error("Unknown service")
            raise ValueError("Unknown service")

        if user_input is not None:
            try:
                user_input[CONF_SERVICE] = service
                platform = Platform.get(service)
                await asyncio.to_thread(
                    platform.validate,
                    user_input[CONF_CF],
                    user_input[CONF_NRE],
                    team=user_input.get(CONF_TEAM),
                    phone=user_input.get(CONF_PHONE),
                )
                return self.async_create_entry(
                    title=user_input[CONF_NRE], data=user_input
                )
            except Exception as e:
                LOGGER.warning(str(e))
                errors["base"] = "invalid_input"
                extras["error_message"] = str(e)

        return self.async_show_form(
            step_id=STEP_INIT,
            data_schema=get_service_schema(service, current_data),
            errors=errors,
            description_placeholders=extras,
        )
