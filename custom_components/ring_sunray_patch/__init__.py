"""Teach python-ring-doorbell about doorbell kinds it does not know yet.

Unknown kinds are reported as "Unknown Doorbell" without the DING and
MOTION_DETECTION capabilities, so Home Assistant creates no ding/motion
event entities for them. Remove this integration once the kinds below ship
in the ring-doorbell version bundled with Home Assistant.
"""

from __future__ import annotations

from base64 import urlsafe_b64decode
import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)

RING_DOMAIN = "ring"
EXTRA_BATTERY_DOORBELL_KINDS = ("doorbell_sunray",)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Patch the kind lists, then reload Ring so it recreates its entities."""
    const, fcmpushclient = await hass.async_add_import_executor_job(_import_modules)

    # Ring sends the crypto-key and salt of its push messages without base64
    # padding; firebase-messaging then raises "Incorrect padding" and shuts
    # its push client down for good, leaving only the slow history polling.
    # The module looks the name up at call time, so replacing it is enough.
    patched_fcm = not getattr(fcmpushclient.urlsafe_b64decode, "_padded", False)
    if patched_fcm:
        fcmpushclient.urlsafe_b64decode = _padded_urlsafe_b64decode
        _LOGGER.info("Patched firebase-messaging base64 decoding")

    # doorbot.py imports these list objects by reference and re-reads them on
    # every has_capability() call, so mutating them in place is enough.
    added = [
        kind
        for kind in EXTRA_BATTERY_DOORBELL_KINDS
        if kind not in const.DOORBELL_BATTERY_KINDS
    ]
    if added:
        const.DOORBELL_BATTERY_KINDS.extend(added)
        _LOGGER.info("Added Ring battery doorbell kinds: %s", ", ".join(added))

    # The reload also restarts a push client that already shut down.
    if not added and not patched_fcm:
        return True

    # Ring may already have created its entities without the patch, and at
    # startup its setup can run concurrently with ours.
    if hass.is_running:
        _reload_ring_entries(hass)
    else:

        @callback
        def _on_started(_event: Event) -> None:
            _reload_ring_entries(hass)

        entry.async_on_unload(
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_started)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the entry; the patch stays in memory until the next restart."""
    return True


def _import_modules():
    from firebase_messaging import fcmpushclient  # noqa: PLC0415
    from ring_doorbell import const  # noqa: PLC0415

    return const, fcmpushclient


def _padded_urlsafe_b64decode(data: bytes | str) -> bytes:
    if isinstance(data, str):
        data = data.encode("ascii")
    return urlsafe_b64decode(data + b"=" * (-len(data) % 4))


_padded_urlsafe_b64decode._padded = True  # type: ignore[attr-defined]


@callback
def _reload_ring_entries(hass: HomeAssistant) -> None:
    for ring_entry in hass.config_entries.async_entries(RING_DOMAIN):
        if ring_entry.state is ConfigEntryState.LOADED:
            hass.config_entries.async_schedule_reload(ring_entry.entry_id)
