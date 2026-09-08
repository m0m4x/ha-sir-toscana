"""Constants for the SIR Toscana integration."""

from datetime import timedelta

DOMAIN = "sir_toscana"

CONF_STATION_ID = "station_id"
CONF_STATION_NAME = "station_name"

BASE_URL = "https://www.sir.toscana.it/monitoraggio"
STATION_URL = BASE_URL + "/actions.php?action=station&id={station_id}"
STATIONS_URL = BASE_URL + "/stazioni.php?type={station_type}"

# Public real-time monitoring tables currently verified on the SIR portal.
# Mareographic stations are also present in the hydrometric table.
STATION_TYPES = (
    "anemo",
    "pluvio",
    "termo",
    "igro",
    "idro",
    "nivo",
)

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=15)
REQUEST_TIMEOUT = 20
