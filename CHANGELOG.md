# Changelog / Project Journey

A dated log of the ANV15-52 Linux tuning work, including the dead ends — because the dead ends
are half the value for anyone reproducing this.

## 2026-06-02 — June regression: RTD3 / power-cap rollback
- **Symptom:** Space Marine 2 (and others) dropped from 90+ fps to ~30 fps; CPU pegged, dGPU
  30–40 % / often <5 %; forced to low quality.
- **Root cause:** the GPU-Guardian "revert" on **2026-06-01 23:03–23:33** disabled the v9 NPCF
  DSDT override and re-enabled NVIDIA RTD3 (`DynamicPowerManagement 0x00 → 0x02`), removing the
  always-on udev rule. The dGPU parked to RTD3/P8 mid-game and `nvidia-powerd` fell back to the
  50 W vBIOS cap → 1219 `SW_POWER_CAP` throttles at only 61 °C (not thermal).
- **Fix:** restored cmdline `0x00`, the `80-nvidia-no-rtd3.rules` udev rule, and the v9 DSDT
  override; rebuilt initramfs. Added dGPU-forcing Steam launch options for hybrid-graphics play.
- Kernel ruled out as a cause (see `docs/kernel-7.0.5-7.0.8-investigation.md`).
- Telemetry proof and full analysis: `docs/gpu-regression-2026-06-spacemarine2.md`.

## NPCF power-cap fix evolution (RTX 5050 50 W → 80 W)
- **v9 (2026-05-31) — current.** Switched from SSDT to a **DSDT override**. Newer ACPICA
  (kernel 7.0.8) hard-errors on the SSDT's duplicate `\_SB.NPCF._DSM` (`AE_ALREADY_EXISTS`), so
  v7/v8 silently stopped applying after the kernel bump. v9 patches the DSDT's `ACBT/ATPP/AMAT`
  budget computation at the source (all `CCOL` branches) so the firmware's own unmodified `_DSM`
  returns the correct TGP. Survives profile/AC-DC transitions. → `acpi/npcf-power-fix/dsdt-npcf.*`
- **v8 (2026-05-29) [superseded].** SSDT; bumped TGP 75 W → 80 W; collapsed a double-load bug to a
  single dracut early-cpio path. → `acpi/npcf-power-fix/history/`
- **v7 (2026-05-24).** SSDT `_DSM` override returning a hardcoded power-budget buffer; first
  correct units (125 mW/unit). → history/
- **v6 (2026-05-24).** First ACPI NPCF attempt; wrong units (10 mW), overwritten by `_Q30`. → history/

## Commit history (original repo)
```
2026-05-25  ANV15-52: fix state-restore errors and silence debug hotkey spam
2026-05-25  docs: ANV15-52 diagnostics & patch notes v1.0
2026-05-25  ANV15-52: fix platform_profile via EC direct path (CCOL/ERM6/_Q30)
2026-05-24  Fix RTX 5050 50W power cap: NPCF SSDT v7 with correct DSM override
2026-05-24  Add game-ready script and enable Resizable BAR for RTX 5050
2026-05-24  Add ACPI NPCF v6 GPU power fix for RTX 5050 on Acer Nitro ANV15-52
2026-05-22  Add CLAUDE.md and hybrid-router run skill
2026-05-22  first commit
```

## 2026-06-02 — repackaged for public release
- Extracted the ANV15-52 work from a private home-directory repo into this dedicated repo.
- Reorganized into `docs/ acpi/ guardian/ nitro-control/ scripts/ linuwu-sense/ diagnostics/`.
- Scrubbed internal infra (IPs, hostnames, email) from shared files.
- Added the GPU-Guardian telemetry dataset (23 sessions) and the nitro-control GUI docs.
