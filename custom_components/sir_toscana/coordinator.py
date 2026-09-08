"""Data update coordinator for SIR Toscana."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SirToscanaApi, SirToscanaApiError
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SirToscanaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate polling of one SIR Toscana station."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: SirToscanaApi,
        station_id: str,
        station_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{station_id}",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.api = api
        self.station_id = station_id
        self.station_name = station_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest complete station payload."""
        try:
            return await self.api.async_get_station_data(self.station_id)
        except SirToscanaApiError as err:
            raise UpdateFailed(
                f"Unable to update SIR Toscana station {self.station_name}"
            ) from err
