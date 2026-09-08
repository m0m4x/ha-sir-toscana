"""Config flow for SIR Toscana."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import SirStation, SirToscanaApi, SirToscanaApiError
from .const import CONF_STATION_ID, CONF_STATION_NAME, DOMAIN


class SirToscanaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SIR Toscana."""

    VERSION = 1

    _stations: list[SirStation] | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        api = SirToscanaApi(async_get_clientsession(self.hass))

        try:
            stations = await self._async_get_stations(api)
        except SirToscanaApiError:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                errors={"base": "cannot_connect"},
            )

        stations_by_id = {station.station_id: station for station in stations}

        if user_input is not None and CONF_STATION_ID in user_input:
            station_id = str(user_input[CONF_STATION_ID])
            station = stations_by_id.get(station_id)

            if station is None:
                errors["base"] = "station_not_found"
            else:
                try:
                    await api.async_get_station_data(station.station_id)
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

        station_options: list[SelectOptionDict] = [
            SelectOptionDict(
                label=f"{station.name} — {station.station_id}",
                value=station.station_id,
            )
            for station in stations
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=station_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _async_get_stations(
        self,
        api: SirToscanaApi,
    ) -> list[SirStation]:
        """Load the station list once for this config flow."""
        if self._stations is None:
            self._stations = await api.async_get_stations()

        return self._stations
