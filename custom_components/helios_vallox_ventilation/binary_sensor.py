import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger("helios_vallox.binary_sensor")


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensors for one Vallox device (AK or YK)."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    prefix = data["prefix"]
    user_conf = data.get("user_conf", {})

    binary_sensor_config = user_conf.get("binary_sensors", [])

    if not binary_sensor_config:
        _LOGGER.warning(
            "No binary_sensors defined in user_conf.yaml for %s",
            entry.data["name"],
        )
        return

    entities = []

    for sensor in binary_sensor_config:
        name = sensor.get("name")
        if not name:
            continue

        entities.append(
            HeliosBinarySensor(
                coordinator=coordinator,
                variable=name,
                prefix=prefix,
                entry=entry,
                description=sensor.get("description"),
                device_class=sensor.get("device_class"),
                icon=sensor.get("icon"),
            )
        )

    async_add_entities(entities, update_before_add=True)


class HeliosBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a single Vallox binary sensor."""

    def __init__(
        self,
        coordinator,
        variable,
        prefix,
        entry,
        description=None,
        device_class=None,
        icon=None,
    ):
        super().__init__(coordinator.coordinator)

        self._coordinator = coordinator
        self._variable = variable
        self._prefix = prefix
        self._entry = entry

        self._attr_name = f"Vallox {prefix.upper()} {variable}"
        self._attr_unique_id = f"vallox_{prefix}_{variable}"

        self._attr_description = description
        self._attr_device_class = device_class
        self._attr_icon = icon

    @property
    def is_on(self):
        if not self._coordinator.coordinator.data:
            return False
        return bool(self._coordinator.coordinator.data.get(self._variable))

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Vallox",
        }
