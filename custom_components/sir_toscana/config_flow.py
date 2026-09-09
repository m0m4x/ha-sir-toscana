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
from .const import (
    CONF_DATA_TYPES,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
    SUPPORTED_DATA_TYPES,
)


class SirToscanaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SIR Toscana."""

    VERSION = 1

    _stations: list[SirStation] | None = None
    _selected_station: SirStation | None = None
    _available_data_types: list[str] | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Select the SIR station."""
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
                    station_data = await api.async_get_station_data(station.station_id)
                except SirToscanaApiError:
                    errors["base"] = "cannot_connect"
                else:
                    available_data_types = [
                        data_type
                        for data_type in SUPPORTED_DATA_TYPES
                        if isinstance(station_data.get(data_type), dict)
                    ]

                    if not available_data_types:
                        errors["base"] = "no_supported_data"
                    else:
                        await self.async_set_unique_id(station.station_id)
                        self._abort_if_unique_id_configured()

                        self._selected_station = station
                        self._available_data_types = available_data_types

                        return await self.async_step_data_types()

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

    async def async_step_data_types(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Select all desired data types available for the station."""
        if self._selected_station is None or self._available_data_types is None:
            return await self.async_step_user()

        errors: dict[str, str] = {}

        if user_input is not None:
            selected_data_types = list(user_input.get(CONF_DATA_TYPES, []))

            if not selected_data_types:
                errors["base"] = "no_data_types_selected"
            else:
                allowed = set(self._available_data_types)
                selected_data_types = [
                    data_type
                    for data_type in selected_data_types
                    if data_type in allowed
                ]

                if not selected_data_types:
                    errors["base"] = "no_data_types_selected"
                else:
                    return self.async_create_entry(
                        title=self._selected_station.name,
                        data={
                            CONF_STATION_ID: self._selected_station.station_id,
                            CONF_STATION_NAME: self._selected_station.name,
                            CONF_DATA_TYPES: selected_data_types,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DATA_TYPES,
                    default=self._available_data_types,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=self._available_data_types,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key=CONF_DATA_TYPES,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="data_types",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "station_name": self._selected_station.name,
            },
        )

    async def _async_get_stations(
        self,
        api: SirToscanaApi,
    ) -> list[SirStation]:
        """Load the station list once for this config flow."""
        if self._stations is None:
            self._stations = await api.async_get_stations()

        return self._stations
