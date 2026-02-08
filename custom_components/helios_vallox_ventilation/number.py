from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class ValloxFanSpeed(CoordinatorEntity, NumberEntity):
    """Fan speed control."""

    def __init__(self, coordinator_wrapper, entry, name):
        super().__init__(coordinator_wrapper.coordinator)

        self._helios = coordinator_wrapper
        self._variable = "fanspeed"
        self._entry = entry

        self._attr_name = f"{name} fan speed"
        self._attr_unique_id = f"{entry.entry_id}_fanspeed"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 8
        self._attr_native_step = 1
        self._attr_icon = "mdi:fan"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=name,
            manufacturer="Vallox / Helios",
            model="Digit SE",
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        return data.get(self._variable)

    async def async_set_native_value(self, value: float):
        await self._helios.async_write_value(self._variable, int(value))


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    name = data["name"]

    async_add_entities([ValloxFanSpeed(coordinator, entry, name)], True)
