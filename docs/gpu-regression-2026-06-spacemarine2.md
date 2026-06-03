# Space Marine 2 / Games — Low GPU Use, Pegged CPU: Root Cause & Fix

**Machine:** Acer Nitro ANV15-52 · RTX 5050 (Blackwell, GB207M) + Intel RPL-P Iris Xe · Ultramarine Linux 44 · KDE/Wayland · NVIDIA 595.71.05
**Symptom (June 2 2026):** CPU pegged, dGPU 30–40% / often <5%, ~30 fps (was 90+ fps high quality May 26–31).

> **Status: primary fix applied 2026-06-02 (pending reboot). Steam launch options below still need to be set per game.**

---

## Active render path (before fix)
- Internal panel `eDP-1` + KDE compositor run on the **Intel iGPU** (`card1`, `0000:00:02.0`); `glxinfo` renderer = Intel RPL-P.
- The RTX 5050's **HDMI port is muxed directly to the dGPU** (`card2-HDMI-A-2`) — which is exactly why the last good session (external monitor over HDMI, Intel off) ran dGPU-native.
- The active Steam launch profile for app 2183900 was the **PYROVEIL** one, which sets **no GPU selector**, so on Wayland Proton/VKD3D defaulted to the **iGPU**.

## Root causes (ranked)

**1. RTD3 power-management regression (highest leverage) — FIXED.**
Guardian's June 1 churn flipped `NVreg_DynamicPowerManagement` to `0x02` and removed the always-on udev rule. `/proc/driver/nvidia/.../power` showed *Runtime D3: Enabled (fine-grained)*. The dGPU kept suspending to P8/RTD3 mid-game and stalling on resume.

**2. NPCF power cap returned to 50W — FIXED.**
The v9 DSDT override (80W cap) was disabled by the same revert, so `nvidia-powerd` fell back to the vBIOS 50W default → constant `SW_POWER_CAP` throttling (1219 events at 61 °C).

**3. Game rendering on the iGPU instead of the dGPU — needs Steam launch options (below).**

### Hard proof (PIXEL-WATCH telemetry, same game/VRAM)
| Metric | May 31 (good) | June 2 (bad) |
|--------|---------------|--------------|
| P8 idle samples | 923 | 3475 |
| SW_POWER_CAP throttles | 46 | **1219** |
| LOOP_STALL events | 0 | ~20 × 8.3 s |
| nvidia-smi latency | normal | up to 512 ms |
| Max temp | 54 °C | 61 °C (not thermal) |

## Fixes
**Applied (system, one reboot):** RTD3 off (`DynamicPowerManagement=0x00` + `80-nvidia-no-rtd3.rules`); v9 NPCF DSDT (80W) re-embedded in initramfs; guardian stopped so it can't re-revert. Backups in `guardian/pre-fix-backup-20260602_231725/`.

**Per-game Steam launch options** (forces the dGPU, enables RT + MangoHud):
```
__NV_PRIME_RENDER_OFFLOAD=1 __VK_LAYER_NV_optimus=NVIDIA_only __GLX_VENDOR_LIBRARY_NAME=nvidia PROTON_ENABLE_NVAPI=1 VKD3D_CONFIG=dxr11,dxr MANGOHUD=1 gamemoderun %command%
```
`prime-run %command%` is a simpler equivalent (it's installed). Replace the PYROVEIL profile, or combine if you still want Pyroveil's shader handling.

## Verify after reboot
1. `cat /proc/driver/nvidia/gpus/*/power` → **Runtime D3 status: Disabled**.
2. `nvidia-smi -q -d POWER` → cap ~80W (not 50W).
3. Launch SM2 → MangoHud shows **"NVIDIA RTX 5050"**, nvidia-smi holds **P0 / ~50–80W / 80–99% util**, fps recovers toward 90+.
4. Next PIXEL-WATCH session should show throttles back near single digits and no `HANG_SUSPECTED`.

## Notes
- On Wayland, hybrid offload to the dGPU for an iGPU-driven panel incurs a reverse-PRIME copy each frame; for max performance, gaming on the **HDMI-out (dGPU-muxed)** external monitor remains the strongest path.
- `nvidia-smi -pl` does **not** work on this GPU (Dynamic Boost owned by `nvidia-powerd` via NPCF) — the DSDT override is the only TGP lever.
