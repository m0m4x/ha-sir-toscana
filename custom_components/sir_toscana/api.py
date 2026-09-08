"""HTTP client for SIR Toscana."""

from __future__ import annotations

import asyncio
import html
import json
import re
from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import REQUEST_TIMEOUT, STATIONS_URL, STATION_TYPES, STATION_URL

_ARRAY_RE = re.compile(
    r'new\s+Array\(\s*"(?P<id>TOS\d+)"\s*,\s*"(?P<name>(?:\\.|[^"])*)"',
    re.IGNORECASE,
)
_TRANSPORT_SUFFIX_RE = re.compile(r"\s+\((?:RADIO|GPRS)\)\s*$", re.IGNORECASE)


class SirToscanaApiError(Exception):
    """Base exception for SIR Toscana API errors."""


class SirToscanaConnectionError(SirToscanaApiError):
    """Raised when SIR Toscana cannot be reached."""


class SirToscanaInvalidResponseError(SirToscanaApiError):
    """Raised when SIR Toscana returns an invalid response."""


class SirToscanaStationNotFoundError(SirToscanaApiError):
    """Raised when a requested station cannot be found."""


class SirToscanaAmbiguousStationError(SirToscanaApiError):
    """Raised when a station name matches more than one station."""


@dataclass(frozen=True, slots=True)
class SirStation:
    """A SIR Toscana station."""

    station_id: str
    name: str


def parse_station_list(text: str) -> list[SirStation]:
    """Extract station identifiers and names from a SIR monitoring page."""
    stations: list[SirStation] = []

    for match in _ARRAY_RE.finditer(text):
        name = match.group("name")
        name = name.replace(r'\"', '"').replace(r"\\", "\\")
        stations.append(
            SirStation(
                station_id=match.group("id"),
                name=html.unescape(name).strip(),
            )
        )

    return stations


def canonical_station_name(value: str) -> str:
    """Normalize a station name for matching across SIR monitoring tables."""
    normalized = " ".join(html.unescape(value).casefold().strip().split())
    normalized = _TRANSPORT_SUFFIX_RE.sub("", normalized)
    return normalized.strip()


class SirToscanaApi:
    """Async client for the public SIR Toscana monitoring endpoints."""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def async_get_station_data(self, station_id: str) -> dict[str, Any]:
        """Return the complete JSON payload for one station."""
        url = STATION_URL.format(station_id=station_id)

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(url)
                response.raise_for_status()
                text = await response.text()
        except (TimeoutError, ClientError) as err:
            raise SirToscanaConnectionError from err

        try:
            data = json.loads(text)
        except json.JSONDecodeError as err:
            raise SirToscanaInvalidResponseError from err

        if not isinstance(data, dict) or not data:
            raise SirToscanaInvalidResponseError

        return data

    async def async_get_stations(self) -> list[SirStation]:
        """Discover station names and IDs from public monitoring tables."""
        stations: dict[str, SirStation] = {}

        results = await asyncio.gather(
            *(
                self._async_get_stations_for_type(station_type)
                for station_type in STATION_TYPES
            ),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, Exception):
                continue

            for station in result:
                current = stations.get(station.station_id)
                if current is None or len(station.name) < len(current.name):
                    stations[station.station_id] = station

        if not stations:
            raise SirToscanaConnectionError

        return sorted(stations.values(), key=lambda station: station.name.casefold())

    async def async_find_station(self, station_name: str) -> SirStation:
        """Find one station by its published name, case-insensitively."""
        requested = canonical_station_name(station_name)
        if not requested:
            raise SirToscanaStationNotFoundError

        stations = await self.async_get_stations()

        exact = [
            station
            for station in stations
            if canonical_station_name(station.name) == requested
        ]
        if len(exact) == 1:
            return exact[0]
        if len(exact) > 1:
            raise SirToscanaAmbiguousStationError

        partial = [
            station
            for station in stations
            if requested in canonical_station_name(station.name)
        ]
        if len(partial) == 1:
            return partial[0]
        if len(partial) > 1:
            raise SirToscanaAmbiguousStationError

        raise SirToscanaStationNotFoundError

    async def _async_get_stations_for_type(
        self,
        station_type: str,
    ) -> list[SirStation]:
        """Read one SIR monitoring table."""
        url = STATIONS_URL.format(station_type=station_type)

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(url)
                response.raise_for_status()
                text = await response.text()
        except (TimeoutError, ClientError) as err:
            raise SirToscanaConnectionError from err

        return parse_station_list(text)
