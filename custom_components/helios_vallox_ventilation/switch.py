import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger("helios_vallox.switch")


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches for one Vallox device (AK or YK)."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    prefix = data["prefix"]  # "yk" or "ak"

    entities = []

    for switch in coordinator.switches:
        name = switch["name"]

        entities.append(
            HeliosSwitch(
                coordinator=coordinator,
                variable=name,
                prefix=prefix,
                entry=entry,
                icon=switch.get("icon"),
                description=switch.get("description"),
            )
        )

    async_add_entities(entities)


class HeliosSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a single Vallox switch."""

    def __init__(
        self,
        coordinator,
        variable,
        prefix,
        entry,
        icon=None,
        description=None,
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
        self._attr_is_on = None

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

    def _handle_coordinator_update(self):
        new_value = self._coordinator.data.get(self._variable)
        if new_value is not None:
            self._attr_is_on = new_value is True or new_value == "on"
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self._coordinator.turn_on(self._variable)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._coordinator.turn_off(self._variable)
        self._attr_is_on = False
        self.async_write_ha_state()
