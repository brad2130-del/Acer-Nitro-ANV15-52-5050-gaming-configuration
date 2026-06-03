#!/usr/bin/env bash
# game-ready.sh — PCIe Gen4, max CPU/GPU performance for gaming (SSDT v8, 80W NPCF)
# Usage: game-ready [on|off]  (default: on)

MODE="${1:-on}"

GPU_PCI="0000:01:00.0"
ROOT_PORT="0000:00:06.0"

case "$MODE" in
  on)
    echo "=== Game Mode: ON ==="

    # Lock PCIe link at Gen 4 x4 — prevent runtime PM from downtraining to Gen 2
    echo on | sudo tee /sys/bus/pci/devices/$GPU_PCI/power/control > /dev/null
    echo on | sudo tee /sys/bus/pci/devices/$ROOT_PORT/power/control > /dev/null
    echo "  PCIe PM: locked to on (prevents Gen2 downtrain)"

    # CPU governor: performance on all cores
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
      echo performance | sudo tee "$cpu" > /dev/null
    done
    echo "  CPU governor: performance"

    # GPU: persistence mode, free boost, +100MHz clock offset for incremental headroom.
    # nvidia-powerd controls the 80W budget (SSDT v8 NPCF TGPA=640=80W).
    sudo nvidia-smi -pm 1 > /dev/null
    sudo nvidia-smi --reset-gpu-clocks > /dev/null 2>&1
    echo "  GPU: persistence on, clocks free"

    # +100MHz boost clock offset via Coolbits (requires reboot after first adding Coolbits
    # to xorg config). Applies on top of nvidia-powerd's boost curve — driver will back off
    # if power budget is exhausted, so this is safe to leave on.
    if nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllFreq=100' > /dev/null 2>&1; then
        echo "  GPU clock offset: +100 MHz"
    else
        echo "  GPU clock offset: not applied (Coolbits may need Xorg restart)"
    fi

    # Power budget: 80W via ACPI NPCF SSDT v8 (TGPA=640=80W)
    echo "  GPU power limit: 80W via ACPI NPCF (SSDT v8)"

    echo ""
    echo "PCIe link speed:"
    sudo lspci -s $ROOT_PORT -vv 2>/dev/null | grep LnkSta | head -1
    echo "GPU power state:"
    nvidia-smi --query-gpu=power.limit,clocks.gr,pstate --format=csv,noheader
    ;;

  off)
    echo "=== Game Mode: OFF ==="

    # Restore PCIe runtime PM
    echo auto | sudo tee /sys/bus/pci/devices/$GPU_PCI/power/control > /dev/null
    echo auto | sudo tee /sys/bus/pci/devices/$ROOT_PORT/power/control > /dev/null
    echo "  PCIe PM: auto (power saving restored)"

    # CPU governor: schedutil (CachyOS default)
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
      echo schedutil | sudo tee "$cpu" > /dev/null
    done
    echo "  CPU governor: schedutil"

    # GPU: clear clock offset and reset to free boost
    nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllFreq=0' > /dev/null 2>&1
    sudo nvidia-smi --reset-gpu-clocks > /dev/null 2>&1
    echo "  GPU: clock offset cleared, free boost restored"
    ;;

  *)
    echo "Usage: game-ready [on|off]"
    exit 1
    ;;
esac
