import logging
import os
import yaml

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import HeliosCoordinator

_LOGGER = logging.getLogger("helios_vallox.__init__")

PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]


async def async_setup(hass: HomeAssistant, config: dict):
    """
    Do nothing here.
    Setup happens via config entries (UI).
    """
    hass.data.setdefault(DOMAIN, {})
    return True


async def _load_user_conf(hass: HomeAssistant, conf_path: str):
    """Read YAML without blocking the event loop."""

    if not os.path.exists(conf_path):
        return None

    def _read_yaml():
        with open(conf_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    try:
        return await hass.async_add_executor_job(_read_yaml)
    except Exception as exc:
        _LOGGER.error("Failed to read user_conf.yaml: %s", exc)
        return {}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up one Vallox device (AK or YK)."""

    ip_address = entry.data["host"]
    port = entry.data.get("port", 502)
    name = entry.data["name"]

    _LOGGER.info("Setting up Vallox device: %s (%s:%s)", name, ip_address, port)

    # ---- READ user_conf.yaml ----
    conf_path = hass.config.path(
        "custom_components",
        "helios_vallox_ventilation",
        "user_conf.yaml",
    )

    user_conf = await _load_user_conf(hass, conf_path)

    if user_conf is None:
        _LOGGER.warning("user_conf.yaml not found, no entities will be created")
        user_conf = {}
    else:
        _LOGGER.info("Loaded user_conf.yaml for %s", name)

    # ---- SET UP coordinator ----
    coordinator = HeliosCoordinator(hass, ip_address, port)
    await coordinator.setup_coordinator()
    await coordinator.coordinator.async_request_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "name": name,
        "prefix": "yk" if "YK" in name else "ak",
        "user_conf": user_conf,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload one Vallox device."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
