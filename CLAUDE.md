# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repo is

Linux tuning & diagnostics for the **Acer Nitro ANV15-52** (i5-13420H, RTX 5050 Blackwell,
Intel Raptor Lake-P iGPU): ACPI/DSDT power-cap overrides, GPU power-management tuning, a
NitroSense-replacement GUI, a telemetry watchdog, raw firmware dumps, and write-ups behind
each fix. There is no "home lab" or MCP-server infrastructure documented here — this repo is
scoped entirely to making this one laptop run well on Linux.

Tested platform: Ultramarine Linux 44, CachyOS kernel `7.0.8-cachyos1`, NVIDIA 595.71.05
(open kernel module).

## Layout

- `docs/` — the write-ups; start here. Notably `npcf-power-cap-fix.md` (RTX 5050 50W→80W fix)
  and `gpu-regression-2026-06-spacemarine2.md` (RTD3/power-cap regression).
- `acpi/npcf-power-fix/` — current v9 DSDT override (`dsdt-npcf.dsl`/`.aml`) + helpers;
  `history/` holds superseded v6-v8 attempts.
- `acpi/raw-dumps/` — raw firmware ACPI tables and disassemblies (reference only).
- `guardian/` — `guardian.py`, an RTD3-aware NVIDIA telemetry poller; `sessions/` holds ~15h
  of logged gaming telemetry (23 sessions, ~41MB JSON) used as evidence in the docs.
- `nitro-control/` — PyQt6 GUI over the `linuwu_sense` sysfs interface.
- `linuwu-sense/` — vendored `acer-wmi` kernel module source (GPL, see its NOTICE.md).
- `scripts/game-ready.sh` — one-shot pre-gaming tuning script.
- `diagnostics/` — freeze diagnostics bundle + logs.

## Working conventions

- These are ACPI/DSDT overrides, kernel-cmdline changes, and EC-level pokes for one specific
  machine. Changes here can affect boot and hardware behavior — be conservative, explain
  what a change does before applying it, and don't guess at ACPI/EC edits without evidence
  from the existing dumps/docs.
- License is GPL-3.0 (consistent with the bundled `linuwu_sense` derivative). Original code
  (`nitro-control/`, `guardian/`, `scripts/`) is also GPL-3.0.
- Telemetry claims in `docs/` are backed by `guardian/sessions/` data — when touching power/
  throttling claims, check the session logs rather than assuming.
