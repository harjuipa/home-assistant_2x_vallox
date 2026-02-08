import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger("helios_vallox.sensor")


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for one Vallox device (AK or YK)."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    prefix = data["prefix"]
    user_conf = data.get("user_conf", {})

    sensor_config = user_conf.get("sensors", [])

    if not sensor_config:
        _LOGGER.warning(
            "No sensors defined in user_conf.yaml for %s", entry.data["name"]
        )
        return

    entities = []

    for sensor in sensor_config:
        name = sensor.get("name")
        if not name:
            continue

        entities.append(
            HeliosSensor(
                coordinator=coordinator,
                variable=name,
                prefix=prefix,
                entry=entry,
                icon=sensor.get("icon"),
                description=sensor.get("description"),
                unit_of_measurement=sensor.get("unit_of_measurement"),
                device_class=sensor.get("device_class"),
                state_class=sensor.get("state_class"),
                min_value=sensor.get("min_value"),
                max_value=sensor.get("max_value"),
                factory_setting=sensor.get("factory_setting"),
            )
        )

    async_add_entities(entities)


class HeliosSensor(CoordinatorEntity, SensorEntity):
    """Representation of a single Vallox sensor."""

    def __init__(
        self,
        coordinator,
        variable,
        prefix,
        entry,
        icon=None,
        description=None,
        unit_of_measurement=None,
        device_class=None,
        state_class=None,
        min_value=None,
        max_value=None,
        factory_setting=None,
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
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_state_class = state_class

        self._attr_min_value = min_value
        self._attr_max_value = max_value
        self._attr_factory_setting = factory_setting

    @property
    def native_value(self):
        if not self._coordinator.coordinator.data:
            return None
        return self._coordinator.coordinator.data.get(self._variable)

    @property
    def extra_state_attributes(self):
        attributes = {
            "min_value": self._attr_min_value,
            "max_value": self._attr_max_value,
            "factory_setting": self._attr_factory_setting,
            "description": self._attr_description,
        }
        return {k: v for k, v in attributes.items() if v is not None}

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Vallox",
        }
