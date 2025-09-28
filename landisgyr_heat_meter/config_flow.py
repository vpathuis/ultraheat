"""Config flow for Landis+Gyr Heat Meter integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import serial
from serial.tools import list_ports
import ultraheat_api
import voluptuous as vol

from homeassistant.components import usb
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, MODEL_T330, SUPPORTED_MODELS, T330_TIMEOUT, ULTRAHEAT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

CONF_MANUAL_PATH = "Enter Manually"
CONF_MODEL = "model"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE): str,
    }
)

STEP_MODEL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODEL): vol.In(SUPPORTED_MODELS),
    }
)


class LandisgyrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ultraheat Heat Meter."""

    VERSION = 3

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.dev_path: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step when setting up serial configuration."""
        errors = {}

        if user_input is not None:
            if user_input[CONF_DEVICE] == CONF_MANUAL_PATH:
                return await self.async_step_setup_serial_manual_path()

            dev_path = await self.hass.async_add_executor_job(
                usb.get_serial_by_id, user_input[CONF_DEVICE]
            )
            _LOGGER.debug("Using this path : %s", dev_path)

            # Store device path and proceed to model selection
            self.dev_path = dev_path
            return await self.async_step_model_selection()

        ports = await get_usb_ports(self.hass)
        ports[CONF_MANUAL_PATH] = CONF_MANUAL_PATH

        schema = vol.Schema({vol.Required(CONF_DEVICE): vol.In(ports)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_setup_serial_manual_path(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set path manually."""
        errors = {}

        if user_input is not None:
            dev_path = user_input[CONF_DEVICE]
            # Store device path and proceed to model selection
            self.dev_path = dev_path
            return await self.async_step_model_selection()

        schema = vol.Schema({vol.Required(CONF_DEVICE): str})
        return self.async_show_form(
            step_id="setup_serial_manual_path",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_model_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step for selecting the heat meter model."""
        errors = {}

        if user_input is not None:
            model = user_input[CONF_MODEL]
            try:
                return await self.validate_and_create_entry(self.dev_path, model)
            except CannotConnect:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="model_selection",
            data_schema=STEP_MODEL_DATA_SCHEMA,
            errors=errors,
        )

    async def validate_and_create_entry(self, dev_path, model):
        """Try to connect to the device path and return an entry."""
        device_number = await self.validate_ultraheat(dev_path, model)

        _LOGGER.debug("Got model %s and device_number %s", model, device_number)
        await self.async_set_unique_id(f"{device_number}")
        self._abort_if_unique_id_configured()
        data = {
            CONF_DEVICE: dev_path,
            "model": model,
            "device_number": device_number,
        }
        return self.async_create_entry(
            title=model,
            data=data,
        )

    async def validate_ultraheat(self, port: str, model: str) -> str:
        """Validate the user input allows us to connect."""

        # Use the appropriate reader based on the model
        if model == MODEL_T330:
            reader = ultraheat_api.T330Reader(port=port, timeout=T330_TIMEOUT)
        else:
            reader = ultraheat_api.UltraheatReader(port=port, timeout=ULTRAHEAT_TIMEOUT)

        heat_meter = ultraheat_api.HeatMeterService(reader)
        try:
            async with asyncio.timeout(ULTRAHEAT_TIMEOUT):
                # validate and retrieve the model and device number for a unique id
                data = await self.hass.async_add_executor_job(heat_meter.read)

        except (TimeoutError, serial.SerialException) as err:
            _LOGGER.warning("Failed read data from: %s. %s", port, err)
            raise CannotConnect(f"Error communicating with device: {err}") from err

        _LOGGER.debug("Successfully connected to %s. Got data: %s", port, data)
        return data.model, data.device_number


async def get_usb_ports(hass: HomeAssistant) -> dict[str, str]:
    """Return a dict of USB ports and their friendly names."""
    ports = await hass.async_add_executor_job(list_ports.comports)
    port_descriptions = {}
    for port in ports:
        # this prevents an issue with usb_device_from_port
        # not working for ports without vid on RPi
        if port.vid:
            usb_device = usb.usb_device_from_port(port)
            dev_path = usb.get_serial_by_id(usb_device.device)
            human_name = usb.human_readable_device_name(
                dev_path,
                usb_device.serial_number,
                usb_device.manufacturer,
                usb_device.description,
                usb_device.vid,
                usb_device.pid,
            )
            port_descriptions[dev_path] = human_name

    return port_descriptions


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
