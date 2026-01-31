import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger("helios_vallox.binary_sensor")


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensors for one Vallox device (AK or YK)."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    prefix = data["prefix"]  # "yk" or "ak"

    entities = []

    for sensor in coordinator.binary_sensors:
        name = sensor["name"]

        entities.append(
            HeliosBinarySensor(
                coordinator=coordinator,
                variable=name,
                prefix=prefix,
                entry=entry,
                icon=sensor.get("icon"),
                description=sensor.get("description"),
                device_class=sensor.get("device_class"),
            )
        )

    async_add_entities(entities)


class HeliosBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a single Vallox binary sensor."""

    def __init__(
        self,
        coordinator,
        variable,
        prefix,
        entry,
        icon=None,
        description=None,
        device_class=None,
    ):
        super().__init__(coordinator.coordinator)

        self._coordinator = coordinator
        self._variable = variable
        self._prefix = prefix
        self._entry = entry

        self._attr_name = f"Vallox {prefix.upper()} {variable}"
        self._attr_unique_id = f"vallox_{prefix}_{variable}"

        self._attr_icon = icon
        self._attr_description = description
        self._attr_device_class = device_class

    @property
    def is_on(self):
        return bool(self._coordinator.data.get(self._variable))

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Vallox",
        }
