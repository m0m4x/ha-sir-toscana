"""Sensor platform for SIR Toscana."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    EntityCategory,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SirToscanaCoordinator

SKIPPED_FIELDS = {"id", "speed_label"}

_PLUVIO_STEP_RE = re.compile(
    r"^CUM(?P<period>24|48)_(?P<start>\d{2})_(?P<end>\d{2})$"
)

_SECTION_LABELS = {
    "anemo": "Anemometro",
    "baro": "Barometro",
    "idro": "Idrometro",
    "igro": "Igrometro",
    "nivo": "Nivometro",
    "pluvio": "Pluviometro",
    "radio": "Radiometro",
    "termo": "Termometro",
}

_CUMULATED_PRECIPITATION_LABELS = {
    "CUM00": "Precipitazioni cumulate 15 minuti",
    "CUM01": "Precipitazioni cumulate 1 ora",
    "CUM03": "Precipitazioni cumulate 3 ore",
    "CUM06": "Precipitazioni cumulate 6 ore",
    "CUM12": "Precipitazioni cumulate 12 ore",
    "CUM24": "Precipitazioni cumulate 24 ore",
    "CUM36": "Precipitazioni cumulate 36 ore",
}

_RETURN_PERIOD_LABELS = {
    "TR01": "Tempo di ritorno precipitazione 1 ora",
    "TR03": "Tempo di ritorno precipitazione 3 ore",
    "TR06": "Tempo di ritorno precipitazione 6 ore",
    "TR12": "Tempo di ritorno precipitazione 12 ore",
    "TR24": "Tempo di ritorno precipitazione 24 ore",
    "TR36": "Tempo di ritorno precipitazione 36 ore",
}


@dataclass(frozen=True, slots=True)
class FieldMetadata:
    """Presentation metadata for one SIR field."""

    name: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    icon: str | None = None
    entity_category: EntityCategory | None = None


def _metadata(section: str, key: str) -> FieldMetadata:
    """Return readable metadata for SIR fields."""
    known: dict[tuple[str, str], FieldMetadata] = {
        ("anemo", "date"): FieldMetadata(
            "Data rilevazione vento",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("anemo", "speed"): FieldMetadata(
            "Velocità vento",
            UnitOfSpeed.METERS_PER_SECOND,
            SensorDeviceClass.WIND_SPEED,
            SensorStateClass.MEASUREMENT,
            "mdi:weather-windy",
        ),
        ("anemo", "dir"): FieldMetadata(
            "Direzione vento",
            DEGREE,
            SensorDeviceClass.WIND_DIRECTION,
            SensorStateClass.MEASUREMENT_ANGLE,
            "mdi:compass",
        ),
        ("baro", "date"): FieldMetadata(
            "Data rilevazione pressione",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("baro", "value"): FieldMetadata(
            "Pressione atmosferica",
            UnitOfPressure.HPA,
            SensorDeviceClass.ATMOSPHERIC_PRESSURE,
            SensorStateClass.MEASUREMENT,
            "mdi:gauge",
        ),
        ("termo", "date"): FieldMetadata(
            "Data rilevazione temperatura",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("termo", "value"): FieldMetadata(
            "Temperatura",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "mdi:thermometer",
        ),
        ("igro", "date"): FieldMetadata(
            "Data rilevazione umidità aria",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("igro", "value"): FieldMetadata(
            "Umidità aria",
            PERCENTAGE,
            SensorDeviceClass.HUMIDITY,
            SensorStateClass.MEASUREMENT,
            "mdi:water-percent",
        ),
        ("radio", "date"): FieldMetadata(
            "Data rilevazione radiometro",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("radio", "value"): FieldMetadata(
            "Radiazione diretta",
            icon="mdi:white-balance-sunny",
        ),
        ("pluvio", "date"): FieldMetadata(
            "Data rilevazione precipitazioni",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    }

    if (section, key) in known:
        return known[(section, key)]

    if section == "pluvio":
        if key in _CUMULATED_PRECIPITATION_LABELS:
            return FieldMetadata(
                _CUMULATED_PRECIPITATION_LABELS[key],
                UnitOfPrecipitationDepth.MILLIMETERS,
                SensorDeviceClass.PRECIPITATION,
                SensorStateClass.MEASUREMENT,
                "mdi:weather-rainy",
            )

        if key in _RETURN_PERIOD_LABELS:
            return FieldMetadata(
                _RETURN_PERIOD_LABELS[key],
                "anni",
                icon="mdi:calendar-clock",
            )

        step_match = _PLUVIO_STEP_RE.match(key)
        if step_match:
            start = step_match.group("start")
            end = step_match.group("end")
            period = step_match.group("period")

            return FieldMetadata(
                f"Precipitazioni step {start}–{end} ({period} h)",
                UnitOfPrecipitationDepth.MILLIMETERS,
                SensorDeviceClass.PRECIPITATION,
                SensorStateClass.MEASUREMENT,
                "mdi:weather-rainy",
            )

    if key == "date":
        section_name = _SECTION_LABELS.get(section, section.title())
        return FieldMetadata(
            f"Data rilevazione {section_name.lower()}",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    section_name = _SECTION_LABELS.get(section, section.title())
    label = key.replace("_", " ").strip().title()

    return FieldMetadata(
        f"{section_name} {label}",
        icon="mdi:chart-line",
    )


def _is_scalar(value: Any) -> bool:
    """Return True for values suitable for a sensor state."""
    return value is None or isinstance(value, (str, int, float, bool))


def _native_value(value: Any) -> Any:
    """Convert numeric strings to numbers while preserving source text."""
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value in ("", "-"):
            return None

        try:
            return float(value)
        except ValueError:
            return value

    return value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SIR Toscana sensors."""
    coordinator: SirToscanaCoordinator = entry.runtime_data
    known_fields: set[tuple[str, str]] = set()

    @callback
    def async_add_new_fields() -> None:
        """Add sensors for fields that appear in the station payload."""
        entities: list[SirToscanaSensor] = []

        for section, section_data in coordinator.data.items():
            if not isinstance(section_data, dict):
                continue

            for key, value in section_data.items():
                field = (section, key)

                if (
                    key in SKIPPED_FIELDS
                    or field in known_fields
                    or not _is_scalar(value)
                ):
                    continue

                known_fields.add(field)

                entities.append(
                    SirToscanaSensor(
                        coordinator=coordinator,
                        section=section,
                        key=key,
                        metadata=_metadata(section, key),
                    )
                )

        if entities:
            async_add_entities(entities)

    async_add_new_fields()
    entry.async_on_unload(coordinator.async_add_listener(async_add_new_fields))


class SirToscanaSensor(CoordinatorEntity[SirToscanaCoordinator], SensorEntity):
    """Representation of one field returned by SIR Toscana."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SirToscanaCoordinator,
        section: str,
        key: str,
        metadata: FieldMetadata,
    ) -> None:
        """Initialize a SIR Toscana sensor."""
        super().__init__(coordinator)

        self._section = section
        self._key = key

        self._attr_unique_id = f"{coordinator.station_id}_{section}_{key}".lower()
        self._attr_name = metadata.name
        self._attr_native_unit_of_measurement = metadata.unit
        self._attr_device_class = metadata.device_class
        self._attr_state_class = metadata.state_class
        self._attr_icon = metadata.icon
        self._attr_entity_category = metadata.entity_category

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.station_id)},
            name=coordinator.station_name,
            manufacturer="Regione Toscana - SIR",
            model="Stazione della rete meteo-idrologica regionale",
            configuration_url="https://www.sir.toscana.it/",
        )

    @property
    def native_value(self) -> Any:
        """Return the latest native value."""
        section_data = self.coordinator.data.get(self._section)

        if not isinstance(section_data, dict):
            return None

        return _native_value(section_data.get(self._key))

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose source identifiers for traceability."""
        return {
            "sir_station_id": self.coordinator.station_id,
            "sir_section": self._section,
            "sir_field": self._key,
            "source": "SIR Toscana",
        }
