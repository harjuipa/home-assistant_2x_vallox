import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import HeliosCoordinator

_LOGGER = logging.getLogger("helios_vallox.__init__")

PLATFORMS = ["sensor", "binary_sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """
    Do nothing here.
    Setup happens via config entries (UI).
    """
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up one Vallox device (AK or YK)."""

    ip_address = entry.data["host"]
    port = entry.data.get("port", 502)
    name = entry.data["name"]

    _LOGGER.info("Setting up Vallox device: %s (%s:%s)", name, ip_address, port)

    coordinator = HeliosCoordinator(hass, ip_address, port)
    await coordinator.setup_coordinator()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "name": name,
        "prefix": "yk" if "YK" in name else "ak",
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload one Vallox device."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
