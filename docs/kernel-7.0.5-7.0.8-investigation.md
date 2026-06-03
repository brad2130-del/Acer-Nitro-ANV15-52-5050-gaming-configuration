# CachyOS Kernel 7.0.5 → 7.0.8 — GPU Regression Investigation

**Machine:** Acer Nitro ANV15-52 · RTX 5050 (Blackwell) + Intel RPL-P · Ultramarine Linux 44 · running `7.0.8-cachyos1.fc44.x86_64`
**Question:** Did a CachyOS kernel point-release (7.0.5→7.0.8) cause the June 2 2026 GPU regression (90+ fps → ~30 fps, GPU underutilized)?

## VERDICT — the kernel is NOT the cause
The regression was caused by the **guardian tool's June 1 (23:03–23:33) config revert**, which disabled the ACPI NPCF power-cap override and re-enabled NVIDIA RTD3 dynamic power management. The running kernel (7.0.8) was already live for the entire good period (May 26–31) and through June 2 — no point-release transition happened in the regression window.

> **Status: FIXED (applied 2026-06-02, pending reboot).** Config restored to known-good; no kernel rollback needed.

---

## (a) Kernels installed + timestamps
| Kernel | rpm installed | vmlinuz | modules finalized |
|--------|---------------|---------|-------------------|
| 7.0.3 | 2026-05-06 17:21 | 2026-05-05 | 2026-05-15 |
| 7.0.5 | 2026-05-10 14:53 | 2026-05-08 | 2026-05-15 |
| **7.0.8** | 2026-05-19 14:23 | 2026-05-18 | **2026-05-25 18:28 (RUNNING)** |

No kernel installed or changed June 1–2. 7.0.8 was the running kernel across the entire good period.

## (b) NVIDIA driver
- Open kernel module **595.71.05**, built 2026-05-19 02:28.
- akmod 2026-05-15; kmod-nvidia(7.0.8) 2026-05-19 14:33; DKMS built for 7.0.3/7.0.5/7.0.8.
- **No June rebuild.** `/var/lib/dkms/nvidia` mtime 2026-05-19.

## (c) Changelog 7.0.5 → 7.0.8
`kernel-cachyos` ships no rpm changelog (empty). Moot regardless: no point-release transition occurred in the regression window — 7.0.8 had been live since May 25.

## (d) Packages updated June 1–2
- **June 1 22:16:** `msr-tools` only (not graphics).
- **June 2 20:42–22:33:** routine batch (systemd 259.6, samba, cups, java, chrome, SDL3, xorg-x11-server 21.1.23, pyqt6) — **no mesa / libdrm / nvidia / vulkan / intel-media / xe / scx**, and it ran *after* the regression was already observed. Mesa 26.1.0 dates to May 21; scx-scheds to May 23 (both pre-good-period).
- May 29 dnf log: repo metadata only, no graphics upgrades.

## (e) The actual cause — guardian's June 1 revert
Good config (`config-backup-20260601_230336`, 23:03) → current live, deltas:
- `nvidia.NVreg_DynamicPowerManagement`: **0x00 → 0x02** (RTD3 dGPU power-down enabled)
- ACPI NPCF override (`99-acpi-override.conf`): **active → DISABLED** (commented; header *"ACPI override DISABLED 2026-06-01 — reverted DSDT injection"*); v9 `dsdt-npcf.aml` moved to `firmware/acpi/retired/`
- `80-nvidia-no-rtd3.rules`: **present → removed**

Runtime proof (`guardian.log` / PIXEL-WATCH): June 2 Space Marine 2 session = **1219 `SW_POWER_CAP` throttle events, max 61 °C, GPU util <5–23%**, plus `HANG_SUSPECTED: GPU util <5% for 20s`. A low-temperature *software* power cap = the NPCF cap returning + RTD3 parking the dGPU — not heat, not a kernel bug.

## Remediation applied
1. Re-enabled ACPI override (`99-acpi-override.conf` → `acpi_override="yes"`); v9 `dsdt-npcf.aml` (80W cap) embedded back into the initramfs (verified checksum `5e369681…`).
2. Restored cmdline `DynamicPowerManagement=0x00` (BLS entry + `/etc/kernel/cmdline`). `RMPlatformRequestHandlerEnable=0` retained via `nvidia-gsp.conf`.
3. Restored `80-nvidia-no-rtd3.rules`.
4. Rebuilt initramfs (`dracut -f`). Pre-fix state backed up to `guardian/pre-fix-backup-20260602_231725/`.

7.0.5 remains installed in GRUB as a control test, but is not needed.
