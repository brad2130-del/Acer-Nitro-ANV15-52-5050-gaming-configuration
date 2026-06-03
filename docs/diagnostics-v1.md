# Acer Nitro ANV15-52 — System Diagnostics & Patch Notes
## v1.0 — Work in Progress

**Platform:** Acer Nitro ANV15-52  
**BIOS:** v1.52 (Dec 26, 2025)  
**Kernel:** 7.0.8-cachyos1.fc44  
**Status:** Active development — patches and findings documented as of BIOS v1.52. As Linux kernel support for Raptor Lake-H + Blackwell matures, new avenues will open and this document will grow.

---

## Why This Document Exists

Getting this laptop to perform correctly on Linux required genuine reverse engineering — not configuration tweaking. There is **no public documentation** for the EC firmware protocol, no upstream kernel quirk for this model, and no community precedent for the RTX 5050 (Blackwell) on Linux at the time this work was done.

Every fix described here was derived from raw ACPI bytecode (53,794-line DSDT), EC register probing, and empirical calibration against hardware behaviour. This document records not just *what* was fixed but *why it was broken*, *what false leads were followed*, and *what can't be fixed yet* — so that future work can build on it rather than repeat it.

---

## Hardware Profile

| Component       | Detail                                                     |
|-----------------|-----------------------------------------------------------|
| Platform        | Acer Nitro ANV15-52                                       |
| CPU             | Intel Core i5-13420H (Raptor Lake-H, 4P+4E, 12 threads)  |
| GPU             | NVIDIA GeForce RTX 5050 Max-Q 8GB (Blackwell GB107)       |
| RAM             | 16GB DDR4-3200 (single SODIMM, dual-channel capable)      |
| Storage         | NVMe SSD                                                  |
| BIOS            | v1.52 (Dec 26, 2025) — fixes dual-channel POST regression |
| OS              | CachyOS, kernel 7.0.8-cachyos1.fc44                       |
| ACPI            | DSDT 53,794 lines; SSDT10 (ACRSYS / ACRPRDCT)            |

---

## The Missing Resources Problem

Before diving into individual fixes, it's worth establishing *why* every problem here required reverse engineering rather than standard configuration. The table below lists what simply does not exist in the public domain for this platform:

| Area | What's Missing |
|------|----------------|
| **NPCF protocol** | No public specification. The UUID `36b49710-2483-11e7-9598-0800200c9a66` is known from scattered ACPI table dumps, but field semantics (units, sub-function IDs, return value structure) had to be calibrated empirically against known-good EC power data. |
| **EC firmware** | No source code, no register map, no documentation. Acer does not publish EC firmware specs. The only access is via the 30-year-old ACPI embedded controller protocol (IO ports 0x62/0x66), which gives single-byte register reads/writes with no schema. |
| **WSMI method IDs** | No public list of which WMI method IDs are implemented in which EC firmware versions. Method `0x000B` (SET_PLATFORM_PROFILE) appears to exist in the DSDT on paper — the EC silently ignores it in practice. There is no error, no log, no indication. |
| **RTX 5050 (Blackwell) Linux maturity** | The RTX 5050 (GB107) launched in early 2026. `nvidia-powerd` Blackwell support, NPCF handshake behaviour for GB1xx silicon, and Optimus power management on Raptor Lake-H are all immature or entirely untested on Linux at time of writing. |
| **Dual-channel POST regression** | The BIOS bug causing POST failure with two RAM sticks was never publicly acknowledged by Acer. v1.52 fixed it silently — no release notes, no advisory. |
| **DPTF thermal object semantics** | Intel's DPTF framework is documented at the architectural level, but Acer's specific ACPI objects (`ODV0`, thermal zone thresholds, DPTF participant names) are entirely proprietary and unlabelled in the DSDT. |
| **ERM6 memory region** | The physical address `0xFE708600` and TUGM field at offset `0x07` were discovered by reading the DSDT's `_Q30` method. There is no other reference to this address anywhere in any public documentation. |

---

## Problem 1: RTX 5050 Hard-Capped at 50W (of 75W TDP)

### Symptoms

- `nvidia-smi` reports Default Power Limit: **50.00 W** (rated 75W TDP)
- GPU performs at roughly 67% of its theoretical throughput under all workloads
- Even in Turbo mode, sustained GPU power never rises above 50W
- `nvidia-smi -pl 75` fails — the limit is enforced below the driver level

### Why This Is Hard to Diagnose on Linux

NVIDIA's laptop power limit negotiation goes through **NPCF (Notebook Power Cap Framework)** — a proprietary Acer/NVIDIA ACPI interface. On Windows, Acer's driver stack writes the correct power budget at runtime. On Linux:

- There is no Linux kernel driver for NPCF
- `nvidia-powerd` exists on Linux but reads ACPI data from NPCF and falls back to defaults when it gets zeros
- The RTX 5050 (Blackwell) is so new that no prior NPCF reverse engineering exists for this silicon generation
- The symptom (50W cap) is identical to what you'd see with a correctly-functioning Max-Q power policy, making it appear intentional

### Root Cause

Found inside `HIDB()` — an ACPI method called by Acer's `_Q30` thermal hotkey handler:

```
// DSDT HIDB() — executes on every thermal profile change
// EC power table for gaming/turbo mode (Mode 4):
//   M1CT = 0  at physical address 0xFE7084A5
//   Therefore: ATPP = 0, ACBT = 0, AMAT = 0, NVWM = 0
//
// nvidia-powerd reads NPCF _DSM sub-function 2 → TGPA=0, ACBT=0
// → interprets as "no platform power budget"
// → falls back to vBIOS Default Power Limit = 50W (Max-Q factory default)
```

The EC's internal gaming-mode power table has `M1CT=0`. This causes the NPCF `_DSM` to return zero for all power budget fields. NVIDIA's daemon sees zeros and treats it as "undefined" rather than "zero watts" — falling back to the conservative vBIOS default.

### The Unit Calibration Discovery

NPCF fields are **not in milliwatts**. The correct unit is **125 mW per unit** (8 units = 1 watt).

This was reverse-engineered by cross-referencing against a working EC mode:
- EC Mode 4 (Performance): `M4CT = 50` → the driver reports this corresponds to ACBT=400
- Cross-check: 400 units × 125mW = 50W — exactly matches `nvidia-smi Default Power Limit`
- Therefore: 75W target = 75 × 8 = **600 units**

An earlier attempt used 10mW/unit, producing `ACBT=7500` (= 937W), which was correctly rejected by the NVIDIA driver. The 125mW/unit discovery was the key breakthrough.

### Fix: SSDT v7 DSM Override

An ACPI SSDT override (`npcf-v7.dsl`, commit `41ebd25`) intercepts NPCF `_DSM` sub-function 2 inside `Scope(_SB.NPCF)` and returns hardcoded `TGPA=600` (75W). All other sub-functions are delegated to the original SSDT14 NPCF() helper — normal operation is preserved.

```
Installed at:
  /usr/lib/firmware/acpi/ssdt-npcf-fix.aml
  /boot/acpi_override.img  (initramfs image)
```

**Verification after boot:**
```bash
dmesg | grep NPCF        # → "NPCFV7   00000007"
nvidia-smi               # → Default Power Limit: 75.00 W
```

**Why the SSDT approach rather than patching the EC power table:** The EC power table at physical address `0xFE7084A5` is mapped into the EC's internal memory — writing to it from Linux would require a live EC firmware patch, which risks rendering the EC unresponsive. The SSDT intercept is clean, reversible, and loads from initramfs before NVIDIA's driver initialises.

---

## Problem 2: Thermal Profiles (platform_profile) Completely Non-Functional

### Symptoms

- Writing to `/sys/firmware/acpi/platform_profile` returns no error
- Reading back the value confirms it "changed" in software
- Fan speed is identical across all profiles
- CPU TDP and GPU power budget are identical across all profiles
- `power-profiles-daemon` / `ppd` has no observable hardware effect

### Why This Required the Deepest Level of Investigation

This problem produced a chain of three plausible-but-wrong leads before the real mechanism was found.

---

#### False Lead 1: The WMI/WSMI Path

The upstream `acer-wmi` driver sends thermal profile changes via `WSMI` — an ACPI method that fires a System Management Interrupt with method ID `0x000B` (SET_PLATFORM_PROFILE). On most Acer Nitro/Predator models this works.

On the ANV15-52, `WSMI` executes without error. The SMI fires. Nothing changes.

**Why:** The EC firmware for this model simply does not implement WSMI method `0x000B`. There is no error return — the call goes into a void. You cannot distinguish "method not implemented" from "method succeeded" at the ACPI level because the EC doesn't respond to it at all.

There is no documentation listing which EC firmware versions implement which WSMI method IDs. The only way to discover this is to fire the SMI and observe whether the hardware responds.

---

#### False Lead 2: CCOL Appears Writable

DSDT analysis of `_Q30` (the Fn hotkey ACPI method) shows it writing to `CCOL` — EC register 0xF4, the authoritative "current thermal mode" field. This looks like a working SET path.

After calling `_Q30` via `acpi_evaluate_object()`, `ec_read(0xF4)` showed CCOL was **unchanged**.

**Why:** CCOL is part of the EC's embedded control address space. From the host side, `ec_write()` goes through the standard ACPI EC bus protocol (IO ports 0x62/0x66). The EC firmware **silently ignores writes to CCOL from the host** — the EC considers CCOL its own internal state register and accepts no external SET commands.

The same applies to `FANT` (EC register 0x54, fan mode table selector). Both registers appear bidirectional in the ACPI table but are read-only from the host's perspective. This is a common embedded controller firmware pattern: registers that track internal state are exposed as readable by the host but silently drop writes.

---

#### False Lead 3: RAPL Changes Don't Appear in Sysfs

When `_Q30` successfully executes, it writes CPU power limits (PPL1/PPL2) to a memory-mapped RAPL region at `GMHB() + 0x5000 + 0x9A0/0x9A4`. After a successful `_Q30` call, `/sys/class/powercap/` showed no change.

**Why:** The Linux kernel manages CPU power limits via **MSR-based RAPL** (MSR `0x610`). Acer's `_Q30` writes to a separate **MMIO-based RAPL path** in the chipset register space (`CPWR` OperationRegion). These are two independent register banks. The kernel's powercap sysfs only exposes the MSR path — the MMIO writes are invisible to standard Linux tooling even when they're taking effect at the hardware level.

---

### The Actual EC Architecture (Discovered via DSDT Analysis)

```
Physical Fn+Mode key pressed
│
├─ EC firmware (internal, not visible to Linux):
│    ├─ Reads physical key state
│    ├─ Writes TUGM (ERM6 region 0xFE708600+0x07) ← mode selector
│    ├─ Writes CCOL (EC register 0xF4) ← EC-side only; host writes ignored
│    └─ Fires ACPI Query 0x30 event
│
└─ ACPI _Q30 method executes (in ACPI interpreter on Linux host):
     ├─ Reads TUGM from ERM6 memory region
     ├─ Attempts CCOL write ← silently ignored by EC
     ├─ Attempts FANT write ← silently ignored by EC
     ├─ Writes PPL1/PPL2 to Intel MMIO RAPL region ← takes effect
     ├─ Calls EC6E(0x83) ← sends fan mode command to EC via IO port 0x6E
     └─ Calls HIDB() ← updates NPCF GPU power budget (ACBT/TGPA/NVWM)
```

**TUGM values and their meaning:**

| TUGM value | _Q30 Switch case | Platform profile |
|------------|-----------------|-----------------|
| 0x00 | Turbo | `performance` |
| 0x01 | Performance | `balanced-performance` |
| 0x02 | Balanced | `balanced` |
| 0x03 | Quiet | `quiet` |
| 0x04 | Eco | `low-power` |

**What software SET actually controls:**

| Effect | Status | Mechanism |
|--------|--------|-----------|
| Intel CPU RAPL power limits | ✅ Applied | _Q30 → MMIO RAPL writes |
| NPCF GPU power budget | ✅ Applied | _Q30 → HIDB() → ACBT/TGPA |
| EC fan curves | ❌ EC-only | EC ignores host writes; responds only to physical Fn key |
| CCOL register update | ❌ Soft shadow | EC-owned; soft shadow maintains GET/SET consistency |

### Key DSDT Objects Discovered

| Object | Location | Role |
|--------|----------|------|
| `CCOL` | EC OperationRegion `VERM`, offset 0xF4 | Current thermal profile (EC-owned) |
| `FANT` | EC OperationRegion `VERM`, offset 0x54, bits[3:0] | Fan mode table selector (EC-owned) |
| `TUGM` | ERM6 SystemMemory `0xFE708600`, offset 0x07 | Mode selector (host-writable) |
| `_Q30` | `\_SB.PC00.LPCB.EC0._Q30` | Fn hotkey ACPI method — applies profile |
| `HIDB()` | `\_SB.PC00.LPCB.EC0.HIDB` | NPCF GPU power update |
| `EC6E(n)` | `\_SB.PC00.LPCB.EC0.EC6E` | EC custom command interface (IO 0x6E) |
| `PPL1/PPL2` | CPWR region `GMHB()+0x5000+0x9A0/0x9A4` | Intel MMIO RAPL |
| `ACBT/TGPA` | NPCF SSDT `_DSM` sub-function 2 | GPU TGP in 125mW units |

### Fix: EC Direct Path + Soft Shadow (commit `8df5fed`)

**New driver quirk:** `quirk_acer_nitro_anv15_52` with `use_ec_profile = 1` — cleanly isolated from all other Acer models in `acer-wmi.c`.

**GET:** `ec_read(0xF4)` reads CCOL directly. Returns `acer_nitro_ec_soft_profile` shadow if a software SET is pending (maintains GET/SET round-trip consistency for `ppd` and `powerprofilesctl`).

**SET:**
1. Map `TUGM` via `ioremap(0xFE708600, 0x100)` and write the TUGM byte for the requested profile
2. Call `\_SB.PC00.LPCB.EC0._Q30` via `acpi_evaluate_object()` — applies MMIO RAPL + NPCF GPU power
3. Cache the requested profile in `acer_nitro_ec_soft_profile` so GET returns the expected value

**Hotkey handler (`acer_thermal_profile_change()`):** On `WMID_GAMING_TURBO_KEY_EVENT` / `key_num=0x5`, reset the soft shadow (the EC has already updated CCOL before the WMI event fired) and call `platform_profile_notify()` so sysfs updates immediately.

### Known Limitation — Fan Curves (Not Fixable Today)

Fan curves change **only** via the physical Fn+Mode key. The EC's thermal management is opaque — it reads its own CCOL register and selects a fan curve from an internal lookup table. There is no documented path to push a new fan curve from Linux without patching the EC firmware binary, which would require physical flash chip access.

The `EC6E(0x83)` command (sent by `_Q30` via IO port 0x6E) may be a partial fan-mode commit command, but the full EC command set for the ANV15-52 is undocumented. This is a target for v2.0 investigation.

---

## Problem 3: CPU Running Below Potential (P-cores Underutilised)

### Symptoms

- `intel_pstate`: active, `governor=performance`, `EPP=performance`, `no_turbo=0`
- P-core boost (up to 4.6GHz) engaging infrequently
- E-cores (max 3.4GHz) handling a disproportionate share of load
- Average P-core clock at roughly 44% of maximum observed

### Root Cause: thermald Fighting a Hybrid CPU

`thermald` (Intel's userspace thermal daemon) was active and enabled. On Raptor Lake-H hybrid architectures, `thermald` uses DPTF (Dynamic Platform Thermal Framework) to manage core activity:

- It can cap P-core turbo headroom via DPTF `ODV0` thermal zone thresholds
- It interprets conservative ACPI thermal limits and biases the scheduler toward E-cores
- It overrides `EPP` settings through its own thermal policy engine
- It was **conflicting with platform_profile** — both modify the same DPTF parameters via ACPI (`HIDB()` in Acer's DSDT writes `ODV0` on every profile change)

With `platform_profile` now genuinely connected to hardware, `thermald` is both redundant and harmful. The correct thermal management stack is:

```
platform_profile driver (hardware-aware EC path)
        ↓
power-profiles-daemon (ppd)
        ↓
EPP / Intel P-state scaling
```

### Fix

```bash
sudo systemctl disable --now thermald
sudo systemctl enable --now power-profiles-daemon
```

This is only safe because `platform_profile` is now genuinely wired to hardware. With the old broken `platform_profile`, removing `thermald` would have left no thermal management at all.

---

## Problem 4: Memory Subsystem

### Single-Channel RAM

The system shipped with one 16GB DDR4-3200 SODIMM in slot `Controller1-ChannelA-DIMM0`. Slot `Controller0-ChannelA-DIMM0` is empty.

The i5-13420H has a **full dual-channel DDR4 memory controller**. The ANV15-52 exposes both channels as independent SODIMM slots (confirmed via SMBIOS: `Number Of Devices: 2`). Despite the system coming from the factory with a single stick in the `Controller1` slot (an unusual slot-selection choice), both channels are fully functional.

This is not a single-channel-only platform. That confusion arises from cheaper Acer laptops with soldered RAM plus one expansion slot — on those, the expansion adds capacity but not channel. The ANV15-52 is not that.

**Single-channel impact:**
- ~50% of theoretical memory bandwidth
- Iris Xe iGPU (which shares system memory) is effectively halved
- Shader compilation, emulation (Dolphin), and streaming workloads are all memory-bandwidth bound

**Fix:** Add a matching 16GB DDR4-3200 SODIMM to the `Controller0` slot. BIOS v1.52 resolved a DRAM training regression that caused POST failures with two sticks.

### ZRAM Swappiness Hidden Override

The system uses ZRAM (compressed in-RAM swap, `zstd`, 7.7GB) instead of disk-based swap. A udev rule at `/usr/lib/udev/rules.d/30-zram.rules` forcibly sets `vm.swappiness=150` when ZRAM initialises — **this fires after all `sysctl.d` files are processed** and silently overrides them.

Any `vm.swappiness` setting in `/etc/sysctl.d/` is a no-op on this system without knowing about this rule.

The system was running with `swappiness=150`, compressing 2.5GB of active memory into ZRAM unnecessarily despite 8GB of free physical RAM.

**Why not `swappiness=10`:** The low-swappiness guideline comes from the era of disk-based swap, where any swap operation means a disk seek. With ZRAM, the equation flips: compressing anonymous pages to ZRAM (fast, in-RAM, CPU-only) is vastly preferable to evicting page cache back to the NVMe. A high swappiness value means "prefer ZRAM for anonymous pages, keep page cache hot" — which is correct for a gaming system on NVMe + ZRAM.

**Fix:** Created `/etc/udev/rules.d/30-zram.rules` (overrides the system rule — `/etc/` takes precedence over `/usr/lib/` for identically-named udev rules). Sets `vm.swappiness=100`.

### sysctl Configuration Consolidation

`/etc/sysctl.d/` had two conflicting files (`99-gaming.conf` and `99-nitro-gaming.conf`) both attempting to set `swappiness=10`, neither succeeding. The `99-nitro-gaming.conf` also had broken `dirty_bytes=0` entries that produced `Invalid argument` errors at boot (you cannot zero the bytes-based dirty thresholds while the system is using them in ratio mode).

Consolidated into a clean `/etc/sysctl.d/99-nitro-gaming.conf`:

| Setting | Value | Reason |
|---------|-------|--------|
| `vm.swappiness` | 100 | ZRAM-aware (udev rule enforces this at runtime) |
| `vm.vfs_cache_pressure` | 50 | Keep dentries/inodes in cache; btrfs benefits greatly |
| `vm.overcommit_memory` | 1 | Games malloc large pools — fail at use, not at alloc |
| `vm.compaction_proactiveness` | 0 | Disable proactive compaction — eliminates mid-game latency spikes |
| `vm.zone_reclaim_mode` | 0 | No NUMA on this system; zone reclaim adds latency for nothing |
| `kernel.numa_balancing` | 0 | Single-socket system; NUMA balancing is irrelevant overhead |
| `kernel.sched_autogroup_enabled` | 1 | Games scheduled as a unit vs competing thread-by-thread |

---

## Current Platform State

| Feature | Status | Notes |
|---------|--------|-------|
| GPU at full 75W TDP | ✅ | SSDT v7 NPCF override; loads via initramfs |
| `platform_profile` GET | ✅ | `ec_read(CCOL)` — reflects real EC state |
| `platform_profile` SET — CPU power | ✅ | TUGM + `_Q30` → MMIO RAPL limits |
| `platform_profile` SET — GPU power | ✅ | `_Q30` → `HIDB()` → NPCF ACBT/TGPA |
| `platform_profile` SET — fan curves | ❌ | EC-only; only physical Fn+Mode key changes fans |
| P-core boost engagement | ✅ | `thermald` disabled; `ppd` manages EPP |
| Resizable BAR | ✅ | Enabled via `game-ready` script |
| Dual-channel RAM | ⏳ | Awaiting 2nd SODIMM in Controller0 slot |
| ZRAM swappiness | ✅ | udev override → 100 |
| sysctl tuning | ✅ | Consolidated, compaction/NUMA/zone_reclaim disabled |

---

## v2.0 Investigation Targets

These require further work as kernel support and tooling mature:

**1. Full fan control via EC command interface**
`EC6E(0x83)` sends mode commands to the EC via IO port 0x6E. Further RE of the EC command protocol (building on the `EC6E`, `IBE2`, `MUT0` analysis in the DSDT) may expose a direct fan curve write path without requiring a physical Fn+Mode keypress. This would complete the `platform_profile` SET implementation.

**2. MMIO RAPL visibility**
`_Q30` writes CPU power limits to `GMHB()+0x5000+0x9A0/0x9A4` (MMIO RAPL). These writes are invisible to `/sys/class/powercap/` because the kernel uses MSR-based RAPL. A custom sysfs node or tracepoint to read back the MMIO RAPL values would allow verification that profile changes are actually taking effect.

**3. Upstream kernel patch**
The ANV15-52 DMI entry and `quirk_acer_nitro_anv15_52` should be submitted to mainline `drivers/platform/x86/acer-wmi.c`. Every ANV15-52 user running Linux currently has silently broken thermal profiles and silently capped GPU power.

**4. Dynamic NPCF power following**
The SSDT currently hardcodes 75W. When the platform_profile is `low-power` or `quiet`, the EC intends a lower GPU budget (35-40W). Hooking NPCF into the profile SET path would make GPU power follow the active profile dynamically rather than always being maximum.

**5. Dual-channel verification and retuning**
After the 2nd SODIMM is installed: run `stream` benchmark to confirm dual-channel, re-tune `dirty_bytes` thresholds for the doubled bandwidth, and re-evaluate ZRAM sizing (with more bandwidth, ZRAM compression overhead matters less).

**6. BIOS diff tracking**
Each BIOS update may change DSDT structure. Keep decompiled DSDT versions under version control and diff between them — particularly watching for changes to `CCOL`, `TUGM`, ERM6 address, and NPCF `_DSM` structure.

---

## Commit History

| Commit | Description |
|--------|-------------|
| `bb61352` | Initial repo — linuwu_sense base, CLAUDE.md |
| `8e4e15a` | ACPI NPCF v6 GPU power fix — *wrong 10mW/unit, rejected by driver* |
| `30631a4` | game-ready script; Resizable BAR enable |
| `41ebd25` | NPCF SSDT v7 — correct 125mW/unit, TGPA=600 (75W) |
| `8df5fed` | platform_profile — EC direct path (CCOL/ERM6/\_Q30), soft shadow |

---

## Reference: Key ACPI Addresses

| Symbol | Address / Path | Description |
|--------|----------------|-------------|
| `CCOL` | EC offset `0xF4` | Current thermal profile (EC-owned read-only from host) |
| `FANT` | EC offset `0x54` bits[3:0] | Fan mode table selector (EC-owned) |
| `TUGM` | `0xFE708600 + 0x07` | Mode selector (host-writable via ioremap) |
| `PPL1` | `GMHB()+0x5000+0x9A0` | Intel MMIO RAPL power limit 1 |
| `PPL2` | `GMHB()+0x5000+0x9A4` | Intel MMIO RAPL power limit 2 |
| `M1CT` | `0xFE7084A5` | EC gaming-mode power table (M1CT=0 causes 50W cap) |
| `_Q30` | `\_SB.PC00.LPCB.EC0._Q30` | Fn hotkey ACPI handler |
| `HIDB` | `\_SB.PC00.LPCB.EC0.HIDB` | NPCF GPU power update method |
| `EC6E` | `\_SB.PC00.LPCB.EC0.EC6E` | EC custom command (IO port 0x6E) |
| `NPCF` | `\_SB.NPCF` | NVIDIA Notebook Power Cap Framework device |
| NPCF UUID | `36b49710-2483-11e7-9598-0800200c9a66` | NPCF _DSM UUID |
| NPCF sub-fn 2 | `_DSM` arg 2 | Returns TGPA/ACBT — GPU TGP in 125mW units |

---

*v1.0 — Acer Nitro ANV15-52 diagnostics and patch notes. BIOS v1.52, kernel 7.0.8-cachyos1.fc44, NVIDIA driver 570.xx. This is a work in progress — updates expected as Linux support for Raptor Lake-H + Blackwell matures and additional EC command paths are investigated.*
