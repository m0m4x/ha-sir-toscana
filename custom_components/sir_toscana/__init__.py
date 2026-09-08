"""SIR Toscana integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SirToscanaApi
from .const import CONF_STATION_ID, CONF_STATION_NAME
from .coordinator import SirToscanaCoordinator

PLATFORMS = (Platform.SENSOR,)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SIR Toscana from a config entry."""
    api = SirToscanaApi(async_get_clientsession(hass))

    coordinator = SirToscanaCoordinator(
        hass=hass,
        entry=entry,
        api=api,
        station_id=entry.data[CONF_STATION_ID],
        station_name=entry.data[CONF_STATION_NAME],
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SIR Toscana config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
