import asyncio
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .vent_functions import HeliosBase

_LOGGER = logging.getLogger("helios_vallox.coordinator")


class HeliosCoordinator:
    """Handles all Modbus communication safely (read + write)."""

    def __init__(self, hass: HomeAssistant, ip: str, port: int):
        self._hass = hass
        self._ip = ip
        self._port = port
        self._lock = asyncio.Lock()

        self._helios = HeliosBase(hass, ip, port)

        # values set by user but not yet confirmed by device
        self._optimistic = {}

        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="Helios Vallox Data Coordinator",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=59),
        )

    @property
    def coordinator(self):
        return self._coordinator

    async def setup_coordinator(self):
        """Connect to device."""
        connected = await self._hass.async_add_executor_job(self._helios._connect)
        if connected:
            await self._coordinator.async_config_entry_first_refresh()
        else:
            _LOGGER.error("Failed to connect to ventilation during setup.")

    # -------------------------
    # READ VALUES
    # -------------------------

    async def _async_update_data(self):
        """Poll all registers safely."""
        async with self._lock:
            try:
                data = await self._hass.async_add_executor_job(
                    self._helios.readAllValues
                )

                if not data:
                    return {}

                # keep optimistic values until device confirms them
                for var, val in list(self._optimistic.items()):
                    device_val = data.get(var)

                    if device_val == val:
                        # device confirmed → stop overriding
                        self._optimistic.pop(var)
                    else:
                        # keep HA UI at user value
                        data[var] = val

                return data

            except Exception as e:
                _LOGGER.error("Error fetching data: %s", e, exc_info=True)
                return {}

    # -------------------------
    # WRITE VALUES
    # -------------------------

    async def async_write_value(self, variable, value) -> bool:
        """Write register and update HA immediately."""

        async with self._lock:
            try:
                # IMPORTANT: Vallox bit writes require current register value first
                # (needed for button commands like winter_mode)
                try:
                    await self._hass.async_add_executor_job(
                        self._helios.readSingleValue, variable
                    )
                except Exception:
                    pass

                result = await self._hass.async_add_executor_job(
                    self._helios.writeValue, variable, value
                )

                if not result:
                    _LOGGER.warning("Write failed: %s -> %s", variable, value)
                    return False

                # remember value until device confirms
                self._optimistic[variable] = value

                # instant UI update
                if self._coordinator.data:
                    new_data = dict(self._coordinator.data)
                    new_data[variable] = value
                    self._coordinator.async_set_updated_data(new_data)

                await asyncio.sleep(0)
                return True

            except Exception as e:
                _LOGGER.error(
                    "Error writing %s to %s: %s", value, variable, e, exc_info=True
                )
                return False

    # -------------------------
    # SWITCH HELPERS
    # -------------------------

    async def turn_on(self, variable):
        await self.async_write_value(variable, 1)

    async def turn_off(self, variable):
        await self.async_write_value(variable, 0)
