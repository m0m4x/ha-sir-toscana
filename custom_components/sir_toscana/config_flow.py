"""Config flow for SIR Toscana."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .api import (
    SirToscanaAmbiguousStationError,
    SirToscanaApi,
    SirToscanaApiError,
    SirToscanaStationNotFoundError,
)
from .const import CONF_STATION_ID, CONF_STATION_NAME, DOMAIN


class SirToscanaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SIR Toscana."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            station_name = str(user_input[CONF_STATION_NAME]).strip()
            api = SirToscanaApi(async_get_clientsession(self.hass))

            try:
                station = await api.async_find_station(station_name)
                await api.async_get_station_data(station.station_id)
            except SirToscanaAmbiguousStationError:
                errors["base"] = "ambiguous_station"
            except SirToscanaStationNotFoundError:
                errors["base"] = "station_not_found"
            except SirToscanaApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(station.station_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=station.name,
                    data={
                        CONF_STATION_ID: station.station_id,
                        CONF_STATION_NAME: station.name,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_NAME): TextSelector(
                    TextSelectorConfig(autocomplete="off")
                )
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
