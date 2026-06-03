# Nitro Control
### A Linux replacement for NitroSense — Acer Nitro ANV15-52

Nitro Control is a native **PyQt6** desktop app that gives Acer Nitro owners on Linux the
hardware controls that Acer only ships in the Windows-only *NitroSense* application: fan
control, power profiles, battery care, LCD overdrive, USB-charge-while-sleeping, boot
animation/sound, and live temperature/RPM telemetry.

It works by talking directly to **sysfs** nodes exposed by the
[`linuwu_sense`](https://github.com/0x7375646F/Linuwu-Sense) kernel module (which binds to
`acer-wmi`). A small root helper invoked through **polkit (`pkexec`)** performs the privileged
sysfs writes, so the GUI itself runs unprivileged.

> Built and tested on an **Acer Nitro ANV15-52** (i5-13420H · RTX 5050) running
> **Ultramarine Linux 44** with the **CachyOS kernel**. Other Nitro models that `linuwu_sense`
> supports may work but are untested.

<!-- TODO: add screenshot -> assets/screenshot.png and reference it here -->

---

## Features

| Feature | Status |
|---------|--------|
| Power profile (`low-power / quiet / balanced / balanced-performance / performance`) | ✅ direct write to `platform-profile` |
| CPU + GPU fan speed (auto, or manual RPM) | ✅ |
| Battery care limit (80% cap) | ✅ |
| LCD overdrive toggle | ✅ |
| USB charging while sleeping | ✅ |
| Boot animation / sound | ✅ |
| Battery calibration trigger | ✅ |
| Live telemetry — CPU/GPU/SYS temps + fan RPM (hwmon) | ✅ (3 s poll) |
| Settings persistence + restore on boot | ⚠️ see [Known Issues](#known-issues--roadmap) |
| GPU power-limit control | ❌ **read-only** (display only; no write path) |
| SCX LAVD scheduler toggle | ❌ **non-functional** (UI checkbox, no backend) |

## Requirements

- Fedora-based distro (built on Ultramarine 44 / CachyOS kernel)
- `linuwu_sense` DKMS module installed and bound to `acer-wmi`
- Python 3.10+
- PyQt6 + PyQt6-WebEngine (`python3-pyqt6`, `python3-pyqt6-webengine` — installed to
  `/usr/bin/python3`, **not** Homebrew Python)
- polkit (`pkexec`)

## Install

```bash
git clone <your-fork-url> nitro-control
cd nitro-control
sudo bash install.sh
nitro-control
```

`install.sh` installs the app to `/usr/local/lib/nitro-control/`, a launcher to
`/usr/local/bin/nitro-control`, the root helper to `/usr/local/bin/nitro-helper`, the polkit
policy, the boot-restore systemd service, and `/etc/modprobe.d/linuwu_sense.conf`
(`nitro_v4=1` + `blacklist acer_wmi`).

## Architecture

```
nitro_control.py      PyQt6 window hosting a QWebEngineView
backend.py            QObject — sysfs reads + settings, bridged to JS via QWebChannel
ui/index.html         HTML/CSS/JS front-end
privileged_helper.py  root helper (via pkexec) that performs sysfs writes
restore_on_boot.py    applies saved settings at boot (systemd service)
install.sh            installer
linuwu_sense.conf     -> /etc/modprobe.d/  (nitro_v4=1, blacklist acer_wmi)
nitro-control-restore.service / com.nitrocontrol.helper.policy / nitro-control.desktop
```

Sysfs paths used:
```
/sys/devices/platform/acer-wmi/nitro_sense/{fan_speed,battery_limiter,usb_charging,
                                            lcd_override,boot_animation_sound,battery_calibration}
/sys/devices/platform/acer-wmi/platform-profile/platform-profile-0/{profile,choices}
/sys/devices/platform/acer-wmi/hwmon/hwmon*/   (temp{1,2,3}_input, fan{1,2}_input)
```

## Technical notes & gotchas (verified against the code)

- **`linuwu_sense` binds to `acer-wmi`**, so controls live under
  `/sys/devices/platform/acer-wmi/…`, not a dedicated platform driver.
- **`nitro_v4=1` is required** — without it the module falls back to hardcoded profiles and fan
  control misbehaves (set in `linuwu_sense.conf`).
- **`acer_wmi` is blacklisted** (same conf) because it races `linuwu_sense` on boot and prevents
  it binding.
- **Power profile is written directly** to the standard 5-value `platform-profile` node
  (`backend.py: set_profile` → `privileged_helper.py`). *Note: on some ANV15-52 EC revisions this
  node returns `EIO` on write — if profiles don't change, that's the EC, and a
  `cycle_gaming_thermal_profile` module-param approach would be needed. The current code does
  **not** implement that cycle workaround.*
- **PyQt6 lives at `/usr/bin/python3`** (dnf packages), not Homebrew's Python.

## Known issues / roadmap

Real, verified in the code — fix before relying on them:

1. **Boot-restore likely targets the wrong home.** `restore_on_boot.py` resolves `Path.home()`,
   but the systemd service runs as **root**, so it looks in
   `/root/.config/nitro-control/settings.json`. The `/etc/nitro-control/settings.json` fallback
   is **never created by the installer** → the boot service silently applies *defaults*, not your
   saved settings. Fix: pass the real user / config path explicitly (`User=`, env var, or
   `--config`).
2. **Launcher uses bare `python3`** (`install.sh:143`), not `/usr/bin/python3`; if a Homebrew
   `python3` is first on `PATH`, the PyQt6 import fails. Pin to `/usr/bin/python3`.
3. **GPU power-limit control is read-only** — UI shows it; there is no write path.
4. **SCX LAVD toggle is a dead checkbox** (`ui/index.html`) — no backend slot.
5. **Single modprobe file only** — load relies on `/etc/modprobe.d/linuwu_sense.conf` plus the
   service's `ExecStartPre=modprobe`; there is no `/etc/modules-load.d/` entry.
6. GPU temp may read 0 at idle — wire `nvidia-smi` into the telemetry poll.
7. `config/` and `assets/` ship empty; add a screenshot to `assets/`.
8. Window height: header can be clipped — bump ~+60px.
9. Do a cold-boot test to confirm the full persistence stack end-to-end.

## Troubleshooting

- **No controls / sysfs missing:** confirm `linuwu_sense` is loaded and bound to `acer-wmi`
  (`ls /sys/devices/platform/acer-wmi/`); ensure `acer_wmi` is blacklisted and `nitro_v4=1`.
- **App won't launch / WebEngine import error:** run `/usr/bin/python3 -c "from
  PyQt6.QtWebEngineWidgets import QWebEngineView"`; install `python3-pyqt6-webengine`.
- **pkexec prompts every time / fails:** check the polkit policy under
  `/usr/share/polkit-1/actions/`.
- **Settings not restored after reboot:** see Known Issue #1.

## License

[GPL-3.0](LICENSE). Interfaces with the GPL-licensed `linuwu_sense` kernel module via sysfs.
