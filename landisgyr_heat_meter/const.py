"""Constants for the Landis+Gyr Heat Meter integration."""

from datetime import timedelta

DOMAIN = "landisgyr_heat_meter"

ULTRAHEAT_TIMEOUT = 30  # reading the IR port can take some time
T330_TIMEOUT = 2
POLLING_INTERVAL = timedelta(days=1)  # Polling is only daily to prevent battery drain.

# Supported models
MODEL_UH50 = "UH50"
MODEL_T550 = "T550"
MODEL_T330 = "T330"

SUPPORTED_MODELS = [MODEL_UH50, MODEL_T550, MODEL_T330]
