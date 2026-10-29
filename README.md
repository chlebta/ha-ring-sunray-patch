# Ring sunray patch

Temporary Home Assistant integration that adds the `doorbell_sunray` kind to
[python-ring-doorbell](https://github.com/python-ring-doorbell/python-ring-doorbell)'s
battery doorbell list at runtime.

Without it, this Ring battery doorbell shows up as "Unknown Doorbell" and the
official Ring integration creates no `event.*_ding` / `event.*_motion` entities.

Upstream fix: [`add-doorbell-sunray`](https://github.com/chlebta/python-ring-doorbell/tree/add-doorbell-sunray).
Uninstall this integration once Home Assistant ships a ring-doorbell release
that includes it.

## Install

1. HACS → Custom repositories → `https://github.com/chlebta/ha-ring-sunray-patch` (Integration).
2. Download **Ring sunray patch**, restart Home Assistant.
3. Settings → Devices & services → Add integration → **Ring sunray patch**.

The Ring integration is reloaded once so it recreates its entities.
