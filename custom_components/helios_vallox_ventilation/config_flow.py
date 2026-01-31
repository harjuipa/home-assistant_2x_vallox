from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "helios_vallox"


class HeliosValloxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(
                "name",
                default="Vallox YK"
            ): vol.In(["Vallox YK", "Vallox AK"]),
            vol.Required("host"): str,
            vol.Required("port", default=502): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
