"""Constants for the SIR Toscana integration."""

from datetime import timedelta

DOMAIN = "sir_toscana"

CONF_STATION_ID = "station_id"
CONF_STATION_NAME = "station_name"
CONF_DATA_TYPES = "data_types"

BASE_URL = "https://www.sir.toscana.it/monitoraggio"
STATION_URL = BASE_URL + "/actions.php?action=station&id={station_id}"
STATIONS_URL = BASE_URL + "/stazioni.php?type={station_type}"

# Public real-time monitoring tables currently verified on the SIR portal.
# Mareographic stations are also present in the hydrometric table.
# The same SIR tables are used to discover stations for the config flow.
SUPPORTED_DATA_TYPES = (
    "anemo",
    "radio",
    "pluvio",
    "termo",
    "igro",
    "idro",
    "nivo",
)

STATION_TYPES = SUPPORTED_DATA_TYPES

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=15)
REQUEST_TIMEOUT = 20
