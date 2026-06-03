# Acer Nitro ANV15-52 — Linux Tuning & Diagnostics

Everything needed to make the **Acer Nitro ANV15-52** (i5-13420H · **RTX 5050** Blackwell ·
Intel Raptor Lake-P iGPU) run *well* on Linux: ACPI power-cap fixes, GPU power-management tuning,
a NitroSense replacement GUI, a telemetry watchdog, raw firmware dumps, and the full diagnostic
write-ups behind each fix.

> **Why this exists:** when this laptop shipped, there was essentially **no Linux tuning data for
> the ANV15-52 / RTX 5050** anywhere. This repo is that missing data — the fixes, the dead ends,
> the ACPI dumps, and ~15 hours of logged GPU telemetry — so the next person doesn't start from
> zero.

**Tested on:** Ultramarine Linux 44 · CachyOS kernel `7.0.8-cachyos1` · NVIDIA 595.71.05 (open
kernel module).

> ⚠️ **Disclaimer:** these are ACPI/DSDT overrides, kernel-cmdline changes, and EC-level pokes for
> *this specific machine*. They can affect boot and hardware behaviour. Read the docs, keep
> backups, and understand a change before applying it. No warranty.

---

## What's fixed here

| Problem | Fix | Details |
|---------|-----|---------|
| RTX 5050 capped at **50W** (throttling despite 320W PSU, cool temps) | **v9 DSDT override** — patch the EC's zeroed GPU TGP at the source so `nvidia-powerd` negotiates the full budget (80W) | [`docs/npcf-power-cap-fix.md`](docs/npcf-power-cap-fix.md), [`acpi/npcf-power-fix/`](acpi/npcf-power-fix/) |
| `platform_profile` write returns `EIO` | EC-direct path (CCOL / ERM6 / `_Q30`) | [`docs/diagnostics-v1.md`](docs/diagnostics-v1.md) |
| 10–70 s freezes on resume | S3 `deep` sleep + driver suspend notifier flags | [`docs/npcf-power-cap-fix.md`](docs/npcf-power-cap-fix.md), [`diagnostics/`](diagnostics/) |
| Resizable BAR off | `nvidia.NVreg_EnableResizableBar=1` | [`scripts/game-ready.sh`](scripts/game-ready.sh) |
| Games on iGPU / dGPU RTD3-parking → low GPU util, low fps | RTD3-off cmdline + always-on udev rule + dGPU Steam launch options | [`docs/gpu-regression-2026-06-spacemarine2.md`](docs/gpu-regression-2026-06-spacemarine2.md) |

## Repository layout

```
docs/                         The write-ups — start here
  npcf-power-cap-fix.md          RTX 5050 50W → 80W: full root-cause (EC tables, NPCF _DSM, DSDT)
  diagnostics-v1.md              ANV15-52 platform diagnostics & patch notes
  gpu-regression-2026-06-...md   June 2026 regression: RTD3/power-cap, Space Marine 2, dGPU offload
  kernel-7.0.5-7.0.8-...md       Kernel investigation (ruling out a kernel cause)
acpi/
  npcf-power-fix/              The CURRENT v9 DSDT override (dsdt-npcf.dsl/.aml) + helpers
    history/                    Superseded attempts (v6→v8 SSDTs) — kept for the record
  raw-dumps/                  Raw firmware ACPI tables (*.dat) + key disassemblies (reference)
guardian/                     GPU-Guardian telemetry watchdog
  guardian.py                   RTD3-aware nvidia metrics poller → PIXEL-WATCH dashboard
  sessions/                     ~15 h of logged gaming telemetry (the dataset, 23 sessions)
nitro-control/                NitroSense replacement — PyQt6 GUI over linuwu_sense sysfs
scripts/game-ready.sh         One-shot "prep for gaming" tuning script
linuwu-sense/                 The acer-wmi sysfs module source this all relies on (see NOTICE)
diagnostics/                  Freeze diagnostics bundle + logs
```

## Quick start

- **Read first:** [`docs/npcf-power-cap-fix.md`](docs/npcf-power-cap-fix.md) explains the headline
  RTX 5050 power-cap fix end to end.
- **Apply the power cap:** build/install the v9 DSDT override from
  [`acpi/npcf-power-fix/`](acpi/npcf-power-fix/) (compile `dsdt-npcf.dsl`, embed via
  `dracut` `acpi_override`). The override patches the EC's zeroed GPU TGP so the firmware's own
  `_DSM` returns the correct budget — no duplicate ACPI object, survives profile/AC-DC changes.
- **GUI control:** see [`nitro-control/README.md`](nitro-control/README.md).
- **Telemetry:** run [`guardian/guardian.py`](guardian/guardian.py) (set `PIXEL_WATCH_URL` to your
  dashboard, or leave it logging locally to `sessions/`).

## The telemetry dataset

[`guardian/sessions/`](guardian/sessions/) holds 23 real gaming sessions (~15 h) sampled at
0.5 s while active: GPU util/clock/power, VRAM, temps, throttle-reason bitmasks, RTD3 power state,
and flagged anomalies (`HANG_SUSPECTED`, `SW_POWER_CAP`). It's the empirical backbone for every
claim in `docs/` — e.g. proving the June regression was a *software* power cap (1219 throttles at
61 °C), not heat. ~41 MB of JSON; large but that's the point.

## Credits & license

- The `acer-wmi` sysfs interface comes from the **Linuwu-Sense** kernel module — see
  [`linuwu-sense/NOTICE.md`](linuwu-sense/NOTICE.md) for attribution/licensing. The bundled source
  is included for reproducibility and may carry local patches.
- **License: [GPL-3.0](LICENSE)** — consistent with the GPL-licensed `linuwu_sense` derivative
  included here. Your original code (nitro-control, guardian, scripts) and the ACPI/telemetry
  artifacts are released under GPL-3.0.
