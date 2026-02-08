import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger("helios_vallox.switch")


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches for one Vallox device (AK or YK)."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    prefix = data["prefix"]
    user_conf = data.get("user_conf", {})

    switch_config = user_conf.get("switches", [])

    if not switch_config:
        _LOGGER.warning(
            "No switches defined in user_conf.yaml for %s",
            entry.data["name"],
        )
        return

    entities = []

    for switch in switch_config:
        name = switch.get("name")
        if not name:
            continue

        entities.append(
            HeliosSwitch(
                coordinator=coordinator,
                variable=name,
                prefix=prefix,
                entry=entry,
                description=switch.get("description"),
                icon=switch.get("icon"),
            )
        )

    async_add_entities(entities, update_before_add=True)


class HeliosSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a single Vallox switch."""

    def __init__(
        self,
        coordinator,
        variable,
        prefix,
        entry,
        description=None,
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
        self._attr_icon = icon

    @property
    def is_on(self):
        if not self._coordinator.coordinator.data:
            return False
        return bool(self._coordinator.coordinator.data.get(self._variable))

    async def async_turn_on(self, **kwargs):
        await self._coordinator.turn_on(self._variable)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._coordinator.turn_off(self._variable)
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Vallox",
        }
