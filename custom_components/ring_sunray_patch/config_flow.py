"""Config flow for Ring sunray patch."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

DOMAIN = "ring_sunray_patch"


class RingSunrayPatchConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single confirmation step: the patch has nothing to configure."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm and create the entry."""
        if user_input is not None:
            return self.async_create_entry(title="Ring sunray patch", data={})
        return self.async_show_form(step_id="user")
