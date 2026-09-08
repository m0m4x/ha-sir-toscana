"""Sensor platform for SIR Toscana."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    EntityCategory,
    UnitOfPrecipitationDepth,
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
    """Return metadata for known SIR fields, with a conservative fallback."""
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
            "Data rilevazione umidità",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("igro", "value"): FieldMetadata(
            "Umidità relativa",
            PERCENTAGE,
            SensorDeviceClass.HUMIDITY,
            SensorStateClass.MEASUREMENT,
            "mdi:water-percent",
        ),
        ("radio", "date"): FieldMetadata(
            "Data radio",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("radio", "value"): FieldMetadata(
            "Valore radio SIR",
            icon="mdi:radio-tower",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        ("pluvio", "date"): FieldMetadata(
            "Data rilevazione pluviometro",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    }

    if (section, key) in known:
        return known[(section, key)]

    if section == "pluvio" and key.startswith("CUM"):
        return FieldMetadata(
            key,
            UnitOfPrecipitationDepth.MILLIMETERS,
            SensorDeviceClass.PRECIPITATION,
            SensorStateClass.MEASUREMENT,
            "mdi:weather-rainy",
        )

    if section == "pluvio" and key.startswith("TR"):
        return FieldMetadata(key, icon="mdi:timer-outline")

    if key == "date":
        return FieldMetadata(
            f"Data {section}",
            icon="mdi:clock-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
        )

    label = key.replace("_", " ").strip().title()
    return FieldMetadata(
        f"{section.title()} {label}",
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
