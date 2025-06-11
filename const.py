import logging

DOMAIN = "soundbar_local"

PLATFORMS = ["media_player", "switch"]

DEFAULT_POLL_INTERVAL = 10  # seconds

CONF_VERIFY_SSL = "verify_ssl"
LOGGER = logging.getLogger(__name__)