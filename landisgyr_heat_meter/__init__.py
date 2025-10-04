"""The Landis+Gyr Heat Meter integration."""

from __future__ import annotations

import logging
from typing import Any

import ultraheat_api

from homeassistant.const import CONF_DEVICE, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_registry import RegistryEntry, async_migrate_entries

from .const import DOMAIN, MODEL_T330, T330_TIMEOUT, ULTRAHEAT_TIMEOUT
from .coordinator import UltraheatConfigEntry, UltraheatCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: UltraheatConfigEntry) -> bool:
    """Set up heat meter from a config entry."""

    _LOGGER.debug("Initializing %s integration on %s", DOMAIN, entry.data[CONF_DEVICE])

    # Use the appropriate reader based on the model
    if entry.data["model"] == MODEL_T330:
        reader = ultraheat_api.T330Reader(
            port=entry.data[CONF_DEVICE], timeout=T330_TIMEOUT
        )
    else:
        reader = ultraheat_api.UltraheatReader(
            port=entry.data[CONF_DEVICE], timeout=ULTRAHEAT_TIMEOUT
        )

    api = ultraheat_api.HeatMeterService(reader)

    coordinator = UltraheatCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: UltraheatConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: UltraheatConfigEntry
) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    # Removing domain name and config entry id from entity unique id's, replacing it with device number
    if config_entry.version == 1:
        hass.config_entries.async_update_entry(config_entry, version=2)

        device_number = config_entry.data["device_number"]

        @callback
        def update_entity_unique_id(
            entity_entry: RegistryEntry,
        ) -> dict[str, Any] | None:
            """Update unique ID of entity entry."""
            if entity_entry.platform in entity_entry.unique_id:
                return {
                    "new_unique_id": entity_entry.unique_id.replace(
                        f"{entity_entry.platform}_{entity_entry.config_entry_id}",
                        f"{device_number}",
                    )
                }
            return None

        await async_migrate_entries(
            hass, config_entry.entry_id, update_entity_unique_id
        )

    # Add model field for entries without it (default to UH50 for backward compatibility)
    if config_entry.version == 2:
        hass.config_entries.async_update_entry(config_entry, version=3)

        if "model" not in config_entry.data:
            new_data = config_entry.data.copy()
            new_data["model"] = "UH50"  # Default to UH50 for backward compatibility
            hass.config_entries.async_update_entry(config_entry, data=new_data)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True
