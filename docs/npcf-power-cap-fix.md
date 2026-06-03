# Acer Nitro ANV15-52 — GPU Power Fix (ACPI NPCF Override)

**System:** Acer Nitro ANV15-52 · i5-13420H · RTX 5050 (Blackwell GB207M)  
**OS:** Ultramarine Linux 44 · Kernel 7.0.8-cachyos1 · NVIDIA 595.71.05  
**Override version:** v9 — **DSDT override** (80W GPU TGP — current fix, 2026-05-31)

> **v9 update (2026-05-31): SSDT approach abandoned — replaced by DSDT override.**
> The v7/v8 SSDT added a *second* `\_SB.NPCF._DSM` alongside the firmware's. On kernel
> 7.0.8-cachyos1 (ACPICA core **20251212**) this is rejected at boot:
> ```
> ACPI BIOS Error (bug): Failure creating named object [\_SB.NPCF._DSM], AE_ALREADY_EXISTS
> ```
> Newer ACPICA hard-errors on duplicate named objects where older builds silently let the
> later definition win — so v8 **silently stopped applying** after the kernel bump. The
> firmware defines `Device (NPCF)` + `_DSM` in **ssdt13** (`OEM ID ACRSYS / Table ID ACRPRDCT`),
> which Acer stamps on ~15 SSDTs sharing the same OEM rev — so it **cannot be uniquely
> overridden** by the initrd table-replacement mechanism.
>
> **Correct fix:** override the **DSDT** (the one uniquely-replaceable table) and patch the
> *source* of the budget. The DSDT computes `NPCF.ACBT = (MxCT * 0x08)` on every profile/power
> change (keyed on `CCOL`); the EC has `M1CT = 0`. We replace all 18 assignments
> (`ACBT/ATPP/AMAT`, every `CCOL` branch) with fixed values — `ACBT = 0x0280` (80W),
> `ATPP = 0x0A00`, `AMAT = 0x0960` — so the firmware's own (unmodified) `_DSM` returns the
> correct TGP and `nvidia-powerd` negotiates the full budget. No duplicate object, survives
> profile/AC-DC transitions.
>
> **Note — `nvidia-smi -pl` does NOT work on this GPU** ("not supported in current scope"):
> Dynamic Boost is owned by `nvidia-powerd` via NPCF. The DSDT path is the *only* lever. A
> safety-net service (`rtx5050-powercap.service`) just guarantees persistence mode +
> `nvidia-powerd` stay up. Build: `/usr/lib/firmware/acpi/dsdt-npcf.aml`, source `dsdt-npcf.dsl`.

> **v8 update (2026-05-29) [SUPERSEDED]:** Bumped GPU TGP cap 75W → **80W** (`ACBT`/`BTGA` = 0x280 = 640 × 125mW).
> Also fixed a load-path bug: the table was loading **twice** (stale v7 via the explicit
> `initrd /acpi_override.img` line *and* v8 via the dracut early-cpio embed), causing two
> conflicting `\_SB.NPCF` definitions and inconsistent boots. Collapsed to a **single load
> path** — the dracut embed (`/etc/dracut.conf.d/99-acpi-override.conf` →
> `/usr/lib/firmware/acpi/ssdt-npcf-fix.aml`). The explicit `initrd` line was removed from the
> BLS entry and `/boot/acpi_override.img` retired. Source of truth: `npcf-v8.dsl`.

---

## Problem

The RTX 5050 was throttling at 50W despite a 75W TDP rating and a 320W AC adapter. Temperature was safe (55–66°C), so thermal limits were not the cause. Guardian session data confirmed: 10+ hours of gaming across multiple sessions showed 100% `SwPowerCap` throttle reason, power capped at exactly 50W.

Additionally: 10–70 second system freezes where cursor moved but apps were unresponsive, caused by broken suspend/resume handling.

### Root Causes

**1. Acer EC power table has zeroed GPU TDP for all gaming modes**

The BIOS EC stores 4 power mode tables (M1–M4) at physical address `0xFE708400`. NPCF fields are computed as:
```
NPCF.ACBT = M1CT * 0x08   (GPU TGP field — 125mW per unit)
```

For the RTX 5050 at 75W, M1CT should be 75. Instead the EC has:
- Mode 1 (Performance/Gaming): **M1CT = 0** → ACBT = 0W ← BROKEN
- Mode 3 (Balanced):           **M3CT = 0** → ACBT = 0W ← BROKEN
- Mode 2 (something):          M2CT = 45 → ACBT = 3.6W (too low)
- Mode 4 (Eco/Silent):         M4CT = 50 → ACBT = 50W (calibration match)

**2. nvidia-powerd reads ACBT=0 and falls back to vBIOS default (50W)**

`nvidia-powerd` calls NPCF `_DSM` sub-function 2 (UUID `36b49710-2483-11e7-9598-0800200c9a66`) to get the platform power budget. Sub-function 2 returns:
- `TGPA = ACBT` = 0 for gaming modes → driver falls back to vBIOS Default Power Limit = **50W**
- This is why `nvidia-smi` shows "Default Power Limit: 50.00 W"

**3. SSDT v6 fix used wrong units (10mW instead of 125mW)**

The v6 SSDT set `ACBT = 0x1D4C = 7500`. At 125mW/unit: `7500 × 125mW = 937.5W` — an absurdly high value that nvidia-powerd correctly rejected. The calibration from the Eco mode (M4CT=50 → ACBT=400 → 50W) confirms the unit is **125mW/unit**.

**4. SSDT v6 `_INI` was overwritten by the DSDT at every power mode change**

The DSDT's EC query handler (`_Q30`) fires on mode key presses and rewrites NPCF fields from the EC M1CT/M1DB/M1CP registers. Even when `_INI` set the correct values at boot, subsequent EC events overwrote them with `M1CT * 8 = 0`.

**5. Conflicting kernel parameters**

Two flags were fighting each other:
- `nvidia.NVreg_EnableGpuFirmware=0` — disables GSP firmware
- `NVreg_RegistryDwords=...EnableGpuFirmware=1` — enables it

Blackwell (RTX 50-series) requires GSP firmware and cannot disable it. Both flags were removed.

**6. Wrong sleep mode (s2idle instead of deep)**

System was using S0 idle (s2idle) for suspend. On wake, the NVIDIA driver failed to handle ACPI D-Notifier events, causing 10–70s freezes. Switching to S3 deep sleep fixed this.

**7. ACPI override infrastructure failures (v5–v6 era)**

- dracut config pointed to a deleted directory
- systemd-boot entry had no `initrd /acpi_override.img` line
- The EC ERM4 register table (`0xFE708400`) stores 8-bit fields, limiting any single field to max 255, making it impossible to represent 75W via `M1CT * 8` in 125mW units (would need M1CT=600, which overflows 8 bits)

---

## Fix Applied (v7)

### Strategy

Instead of patching ACBT (which gets overwritten by the DSDT), override the NPCF `_DSM` method itself to intercept sub-function 2 and return a hardcoded correct power budget buffer. This is immune to DSDT overwrites because the response is computed at call-time, not from the field values.

### SSDT v7 — `npcf-v7.dsl`

**Two-layer defense:**

1. **`_INI`** (belt-and-suspenders): sets ACBT=600, AMAT=2400, ATPP=2560, DCBT=400, NVWM=1 at device initialization with correct 125mW/unit values.

2. **`_DSM` override** (the real fix): intercepts NVIDIA NVPCF UUID sub-function 2 and calls `PWBG()` which returns a hardcoded 49-byte buffer with:
   - `TGPA = 600` → 75W GPU TGP on AC (600 × 125mW)
   - `TGPD = 400` → 50W GPU TGP on DC/battery
   - `TPPA = 2560` → 320W total platform power AC
   - `BTPD = 400` → 50W total platform DC
   - `BMGA = 2400` → 300W AC max total

All other NPCF sub-functions (0, 1, 3, 4, 5) are delegated to the original `\_SB.NPCF.NPCF` helper method from SSDT14, so existing behaviour is preserved.

### Expected outcome after reboot

```bash
sudo dmesg | grep -i "NPCFV7\|NPCFIX"
# → ACPI: SSDT ... (v02 BRAD   NPCFV7   00000007 INTL ...)

nvidia-smi -q | grep "Power Limit"
# → Default Power Limit: 75.00 W  (was 50.00 W)
# → Max Power Limit:     75.00 W
```

### Other Fixes Applied (during v5–v6 work)

**Kernel Parameters (`/etc/default/grub`):**
- Removed: `nvidia.NVreg_EnableGpuFirmware=0`, `EnableGpuFirmware=1` from RegistryDwords
- Added: `nvidia.NVreg_EnableS0ixPowerManagement=1`, `nvidia.NVreg_DynamicPowerManagement=0x02`, `mem_sleep_default=deep`, `nvidia.NVreg_EnableResizableBar=1`

**Dracut Config (`/etc/dracut.conf.d/99-acpi-override.conf`):**
```
acpi_override="yes"
acpi_table_dir="/usr/lib/firmware/acpi/"
```

**Boot Entry (`/boot/loader/entries/...-7.0.8-cachyos1.fc44.x86_64.conf`):**
```
initrd /acpi_override.img
initrd /initramfs-7.0.8-cachyos1.fc44.x86_64.img $tuned_initrd
```

---

## NPCF Field Units

| Field | Unit | Formula | Example |
|-------|------|---------|---------|
| ACBT (GPU TGP AC) | 125 mW | W × 8 = units | 75W → 600 |
| DCBT (GPU TGP DC) | 125 mW | W × 8 = units | 50W → 400 |
| AMAT (AC max total) | 125 mW | W × 8 = units | 300W → 2400 |
| ATPP (total platform AC) | 125 mW | W × 8 = units | 320W → 2560 |
| DTPP (total platform DC) | 125 mW | W × 8 = units | 50W → 400 |

Calibration confirmed from EC ERM4: Mode 4 (Eco) has M4CT=50, giving ACBT=400=50W, which exactly matches `nvidia-smi` "Default Power Limit: 50.00 W".

---

## Verification

After reboot, confirm with:

```bash
# SSDT v7 loaded
sudo dmesg | grep -i "NPCF"
# [    0.005xxx] ACPI: Table Upgrade: install [SSDT-BRAD  -NPCFV7  ]

# GPU now has 75W default (was 50W)
nvidia-smi --query-gpu=power.limit,power.default_limit,power.max_limit --format=csv,noheader

# Guardian session during gaming — check max power > 60W
# sessions/session_*.json → power_w field should reach 70-75W
```

---

## Guardian Session Analysis

Guardian collects GPU metrics every 0.5s. Pre-v7 sessions showed:
- 100% throttle reason: `SwPowerCap` (code 4)
- Max power draw: 52W (vBIOS 50W default + measurement noise)
- Avg power during throttle: 40-46W (predictive throttle before hitting cap)
- Temperature during throttle: 60-66°C (well below thermal limits — this was NOT thermal throttle)

With v7: expect max power to reach 70-75W and throttle events to decrease significantly.

---

## File Map

| File | Purpose |
|------|---------|
| `npcf-v8.dsl` | SSDT v8 source — **the source of truth** (80W) |
| `npcf-v8.aml` | Compiled AML for v8 (recompile with `iasl -tc npcf-v8.dsl`) |
| `npcf-v7.*` | Renamed to v8 (2026-05-29); old 75W content superseded |
| `npcf-320w-fresh.dsl` | Old v6 source (wrong units — kept for reference) |
| `/usr/lib/firmware/acpi/ssdt-npcf-fix.aml` | Live AML embedded by dracut (now v8) — **single load path** |
| `/etc/dracut.conf.d/99-acpi-override.conf` | Dracut ACPI override config (the one load mechanism) |
| `/boot/loader/entries/...-7.0.8-...conf` | systemd-boot entry — explicit `initrd /acpi_override.img` line **removed** |
| `/etc/default/grub` | Kernel parameters (RTD3 now disabled: `DynamicPowerManagement=0x00`) |
| `/etc/udev/rules.d/80-nvidia-no-rtd3.rules` | Pins dGPU + root port `power/control=on` |
| `guardian/sessions/` | GPU telemetry from gaming sessions |

---

## Notes for Future Kernel Updates (v9 / DSDT override)

The fix now loads via dracut's early-cpio embed of **`/usr/lib/firmware/acpi/dsdt-npcf.aml`**
(a full patched DSDT), configured in `99-acpi-override.conf`. The old `ssdt-npcf-fix.aml` is
retired to `/usr/lib/firmware/acpi/retired/` — do **not** re-enable it (causes
`AE_ALREADY_EXISTS`). A new kernel gets the DSDT automatically on its `dracut` run; force if
needed:

```bash
sudo dracut --force /boot/initramfs-<new-kernel>.img <new-kernel>
# verify exactly the patched DSDT is embedded (and no SSDT npcf):
sudo lsinitrd /boot/initramfs-<new-kernel>.img | grep firmware/acpi   # → dsdt-npcf.aml only
```

**Rebuilding the DSDT (if BIOS update changes it, or to change the cap).** The DSDT must be
re-derived from the *current* firmware after any BIOS update:
```bash
cd /tmp && sudo acpidump -b && iasl -d dsdt.dat            # dump + disassemble live DSDT
sed -i -E \
  -e 's/NPCF\.AMAT = \(M[0-9]DB \* 0x08\)/NPCF.AMAT = 0x0960/g' \
  -e 's/NPCF\.ATPP = \(M[0-9]CP \* 0x08\)/NPCF.ATPP = 0x0A00/g' \
  -e 's/NPCF\.ACBT = \(M[0-9]CT \* 0x08\)/NPCF.ACBT = 0x0280/g' dsdt.dsl
iasl dsdt.dsl                                              # must report 0 Errors
sudo cp dsdt.aml /usr/lib/firmware/acpi/dsdt-npcf.aml
sudo dracut --force /boot/initramfs-"$(uname -r)".img "$(uname -r)"
```
`ACBT = 0x0280` is 640 × 125mW = **80W**; adjust the hex for a different cap (W × 8).

**Revert:** a pre-change initramfs backup is at
`/boot/initramfs-<kver>.img.pre-npcf-dsdt.bak` — restore it and rebuild to drop the override.
