# Contributing to Nitro Control

Thanks for helping make Linux a first-class citizen on Acer Nitro hardware.

## Project layout

```
nitro_control.py      PyQt6 window (QWebEngineView host)
backend.py            QObject bridged to JS via QWebChannel — sysfs reads + settings
ui/index.html         front-end (HTML/CSS/JS)
privileged_helper.py  root helper invoked via pkexec — the only thing that writes sysfs
restore_on_boot.py    systemd boot-restore
install.sh            installer
```

## Running from source (dev)

```bash
/usr/bin/python3 nitro_control.py          # use system python (PyQt6 is dnf-installed there)
```

You need `linuwu_sense` loaded and bound to `acer-wmi`, plus `python3-pyqt6` and
`python3-pyqt6-webengine`.

## Privileged writes

All sysfs writes go through `privileged_helper.py` via `pkexec`. When adding a new control:

1. Add the sysfs path + node name to the allow-list in `privileged_helper.py`.
2. Add the read in `backend.py` and a setter that calls the helper.
3. Wire the UI control in `ui/index.html` to a `backend` slot via QWebChannel.
4. Never write sysfs directly from the GUI process — keep the privilege boundary at the helper.

## Testing sysfs / polkit changes

- Test the helper directly: `nitro-helper write <node> <value>` (and `read`).
- Re-run `sudo bash install.sh` after changing the polkit policy or modprobe conf.
- Cold-boot test after touching `restore_on_boot.py` or the systemd unit (see README Known
  Issue #1 — the boot-restore home-dir resolution).

## Conventions

- Keep changes accurate to what the hardware/EC actually does on the ANV15-52; document any
  model-specific quirks in the README "Technical notes" section rather than hard-coding silently.
- One logical change per PR; describe what you tested on which hardware/kernel.
- Don't claim a feature works until verified on real hardware — see the README Feature table for
  the honest current status.

## Good first issues

The README "Known issues / roadmap" list is the backlog — items 1, 2, and 6 are the
highest-impact starting points.
