from homeassistant import config_entries
from .const import DOMAIN

class WiloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Wilo config flow."""
    VERSION = 1