#!/usr/bin/env python3
"""
GPU Guardian Agent — Acer Nitro V15 (RTX 5050 Blackwell)
Watches for nvidia GPU processes, feeds metrics to a PIXEL-WATCH dashboard.
Zero config: launches with gaming, sleeps when idle.
"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# ── Config ────────────────────────────────────────────────────────────────────
PIXEL_WATCH_URL = os.environ.get("PIXEL_WATCH_URL", "http://127.0.0.1:8002")  # set to your dashboard host
ACTIVE_INTERVAL  = 0.5   # seconds between metric polls while gaming
IDLE_INTERVAL    = 5.0   # seconds between polls while idle
SESSION_DIR      = Path(__file__).parent / "sessions"
LOG_FILE         = Path(__file__).parent / "guardian.log"
FIXES_DIR        = Path(__file__).parent / "fixes"

# RTX 5050 dGPU — used for RTD3-aware polling (read power state WITHOUT waking the GPU)
GPU_PCI          = os.environ.get("GUARDIAN_GPU_PCI", "0000:01:00.0")
RUNTIME_STATUS   = Path(f"/sys/bus/pci/devices/{GPU_PCI}/power/runtime_status")

# Thresholds (Guardian side — local fast checks)
THRESH_TEMP_WARN  = 83    # °C
THRESH_VRAM_PCT   = 87    # % of total VRAM
THRESH_HANG_SECS  = 20    # seconds GPU util < 5% during active session to suspect hang
THRESH_SMI_LAT    = 1.0   # s — nvidia-smi call slower than this = GPU wake/resume stall
THRESH_LOOP_STALL = 2.0   # s — a poll loop overrunning this = desktop stall (the freeze you feel)

# Process names that indicate gaming (lower-case match)
GAME_HINTS = {
    "wine", "proton", "pressure-vessel", "gamescope",
    "dolphin-emu", "cemu", "rpcs3", "pcsx2", "yuzu", "ryujinx",
    "lutris", "heroic", "mangohud",
}

# GPU-using system/compositor processes that are NOT the game
SYSTEM_PROCS = {
    "kwin_wayland", "kwin_x11", "kwin",
    "xorg", "xwayland",
    "gnome-shell", "plasmashell", "latte-dock",
    "steamwebhelper", "steam",   # Steam UI — not the game
    "gnome-session-b", "gnome-session",
    "pipewire", "wireplumber",
    "discord", "firefox", "chrome", "chromium",
}

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE),
    ]
)
log = logging.getLogger("guardian")

# ── Power-state / throttle helpers ──────────────────────────────────────────────
def gpu_runtime_status() -> str:
    """Read dGPU PCI runtime-PM status from sysfs WITHOUT waking the GPU.
    Returns 'active', 'suspended', 'suspending', 'resuming', or 'unknown'.
    Used to gate nvidia-smi calls: polling a suspended GPU forces an RTD3 wake,
    which both defeats power saving and can induce resume-stall micro-hitches."""
    try:
        return RUNTIME_STATUS.read_text().strip()
    except Exception:
        return "unknown"


# nvidia-smi clocks_throttle_reasons.active bitmask → human-readable flags
THROTTLE_FLAGS = [
    (0x0000000000000001, "GPU_IDLE"),
    (0x0000000000000002, "APP_CLOCKS_SETTING"),
    (0x0000000000000004, "SW_POWER_CAP"),          # power budget (NPCF cap) is biting
    (0x0000000000000008, "HW_SLOWDOWN"),
    (0x0000000000000010, "SYNC_BOOST"),
    (0x0000000000000020, "SW_THERMAL_SLOWDOWN"),
    (0x0000000000000040, "HW_THERMAL_SLOWDOWN"),
    (0x0000000000000080, "HW_POWER_BRAKE_SLOWDOWN"),
    (0x0000000000000100, "DISPLAY_CLOCK_SETTING"),
]


def decode_throttle(bitmask: int) -> list[str]:
    return [name for bit, name in THROTTLE_FLAGS if bitmask & bit]


def recent_nvrm_errors(since: str = "-15min") -> list[str]:
    """Recent NVRM / PlatformRequestHandler kernel errors — correlates stalls with
    the known SBIOS power-handshake failures. Best-effort; empty on failure."""
    try:
        out = subprocess.check_output(
            ["journalctl", "-k", "--since", since, "--no-pager", "-q"],
            timeout=3, text=True
        )
    except Exception:
        return []
    hits = [l.strip() for l in out.splitlines()
            if "NVRM" in l or "PlatformRequestHandler" in l]
    return hits[-10:]


# ── nvidia-smi helpers ────────────────────────────────────────────────────────
METRICS_QUERY = (
    "temperature.gpu,"
    "utilization.gpu,"
    "utilization.memory,"
    "memory.used,"
    "memory.free,"
    "memory.total,"
    "power.draw,"
    "power.limit,"
    "clocks.current.graphics,"
    "clocks.current.memory,"
    "clocks_throttle_reasons.active,"
    "pstate"
)

def get_gpu_metrics() -> dict | None:
    """Return current RTX 5050 metrics as a dict, or None on failure.

    Also times the nvidia-smi call itself: a call that blocks far longer than
    usual means the GPU stalled waking from RTD3 — the signature of the freeze."""
    t0 = time.perf_counter()
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--query-gpu={METRICS_QUERY}",
             "--format=csv,noheader,nounits"],
            timeout=8, text=True
        ).strip()
    except Exception:
        return None
    smi_latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    parts = [p.strip() for p in out.split(",")]
    if len(parts) < 12:
        return None

    def _f(v):
        try: return float(v)
        except: return 0.0

    temp        = _f(parts[0])
    gpu_util    = _f(parts[1])
    mem_util    = _f(parts[2])
    mem_used    = _f(parts[3])
    mem_free    = _f(parts[4])
    mem_total   = _f(parts[5])
    power_draw  = _f(parts[6])
    power_limit = _f(parts[7])
    gpu_clock   = _f(parts[8])
    mem_clock   = _f(parts[9])
    throttle_raw = parts[10].strip()
    pstate      = parts[11].strip()   # e.g. "P0" (max) … "P8" (idle/RTD3)

    # throttle_reasons is hex bitmask; 0x0 = no throttle
    try:
        throttle_int = int(throttle_raw, 16)
    except Exception:
        throttle_int = 0

    vram_pct = round(mem_used / mem_total * 100, 1) if mem_total else 0

    return {
        "ts":            datetime.now(timezone.utc).isoformat(),
        "temp_c":        temp,
        "gpu_util":      gpu_util,
        "mem_util":      mem_util,
        "vram_used":     mem_used,
        "vram_free":     mem_free,
        "vram_total":    mem_total,
        "vram_pct":      vram_pct,
        "power_w":       power_draw,
        "power_limit":   power_limit,
        "gpu_clock":     gpu_clock,
        "mem_clock":     mem_clock,
        "throttle":      throttle_int,
        "throttled":     throttle_int != 0,
        "throttle_flags": decode_throttle(throttle_int),
        "pstate":        pstate,
        "runtime_status": gpu_runtime_status(),
        "smi_latency_ms": smi_latency_ms,
    }


def get_nvidia_procs() -> list[dict]:
    """Return list of processes currently using the nvidia GPU, sorted by SM% descending."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "pmon", "-c", "1", "-s", "u"],
            timeout=3, text=True
        )
    except Exception:
        return []

    # pmon columns: gpu_idx  pid  type  sm%  mem%  enc%  dec%  jpg%  ofa%  command
    procs = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[1])
            if pid <= 0:
                continue
        except ValueError:
            continue
        try:
            sm_pct = int(parts[3])
        except ValueError:
            sm_pct = 0
        name = parts[-1]
        procs.append({"pid": pid, "name": name, "sm": sm_pct})

    # Highest SM% first — the game will dominate
    procs.sort(key=lambda p: p["sm"], reverse=True)
    return procs


_WINE_BINS = {"wine", "wine64", "wine-preloader", "wine32", "wineserver",
              "pressure-vessel-wrap", "proton"}


def _resolve_game_name(pid: int) -> str | None:
    """
    Resolve the real game name for a pid.

    For Wine/Proton processes: reads /proc/pid/cmdline and extracts the last
    Windows .exe argument (e.g. 'Warhammer 40000 Space Marine 2 - Retail.exe'
    → 'Space Marine 2').

    For native processes: returns the executable name from /proc/pid/exe.

    Returns None if the pid is gone or unreadable.
    """
    try:
        exe_name = Path(os.readlink(f"/proc/{pid}/exe")).name
    except Exception:
        return None

    if exe_name.lower() in _WINE_BINS or "wine" in exe_name.lower() or "proton" in exe_name.lower():
        # Wine/Proton — pull the Windows .exe from cmdline.
        # /proc/pid/cmdline separates args with null bytes; splitting on \x00 preserves
        # paths that contain spaces (e.g. "Warhammer 40000 Space Marine 2 - Retail.exe").
        try:
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
            args = [a.decode(errors="replace") for a in raw.split(b"\x00") if a]
            exe_args = [a for a in args if a.lower().endswith(".exe")]
            if exe_args:
                win_path = exe_args[-1]
                game_exe = win_path.replace("\\", "/").split("/")[-1]
                return Path(game_exe).stem
        except Exception:
            pass
        return exe_name  # fall back to wine binary name

    return exe_name


def classify_session(procs: list[dict]) -> str:
    """
    Return a label for the gaming session.

    Strategy (in priority order):
    1. Skip known system/compositor processes.
    2. Prefer any process matching GAME_HINTS (wine, proton, etc.).
    3. Otherwise take the highest-SM non-system process and resolve its real name.
    4. Fall back to highest-SM process name regardless.
    """
    # Filter to non-system procs, preserving SM% order (highest first)
    game_procs = [p for p in procs if p["name"].lower() not in SYSTEM_PROCS]

    # Check hint matches first (proton, wine, etc.) — resolve their real game name
    for p in game_procs:
        for hint in GAME_HINTS:
            if hint in p["name"].lower():
                name = _resolve_game_name(p["pid"])
                return name if name else p["name"]

    # Take the highest-SM non-system process and try to resolve it
    if game_procs:
        p = game_procs[0]
        name = _resolve_game_name(p["pid"])
        return name if name else p["name"]

    # Everything is a system process — fall back to highest-SM overall
    if procs:
        p = procs[0]
        name = _resolve_game_name(p["pid"])
        return name if name else p["name"]

    return "unknown"

# ── Fix actions ───────────────────────────────────────────────────────────────
def apply_fix(fix_name: str, metrics: dict) -> str:
    """Run a fix script and return its output."""
    script = FIXES_DIR / f"{fix_name}.sh"
    if not script.exists():
        return f"fix script not found: {fix_name}"
    try:
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "GPU_TEMP": str(metrics.get("temp_c", 0)),
                 "VRAM_PCT": str(metrics.get("vram_pct", 0))}
        )
        return (result.stdout + result.stderr).strip()
    except Exception as e:
        return str(e)

# ── PIXEL-WATCH HTTP client ───────────────────────────────────────────────────
def pw_post(path: str, data: dict) -> dict | None:
    """POST to PIXEL-WATCH. Returns response dict or None."""
    if not REQUESTS_OK:
        return None
    try:
        r = requests.post(f"{PIXEL_WATCH_URL}{path}", json=data, timeout=4)
        return r.json() if r.ok else None
    except Exception:
        return None


def pw_get(path: str) -> dict | None:
    if not REQUESTS_OK:
        return None
    try:
        r = requests.get(f"{PIXEL_WATCH_URL}{path}", timeout=4)
        return r.json() if r.ok else None
    except Exception:
        return None

# ── Session management ────────────────────────────────────────────────────────
def start_session(procs: list[dict]) -> dict:
    session_id = str(uuid.uuid4())[:8]
    game = classify_session(procs)
    session = {
        "session_id":  session_id,
        "game":        game,
        "start_ts":    datetime.now(timezone.utc).isoformat(),
        "end_ts":      None,
        "metrics":     [],
        "alerts":      [],
        "fixes_applied": [],
        "pids":        [p["pid"] for p in procs],
        "all_gpu_procs": [{"pid": p["pid"], "name": p["name"], "sm": p["sm"]} for p in procs],
        "nvrm_errors_at_start": recent_nvrm_errors(),
    }
    log.info(f"SESSION START  id={session_id}  game={game}  "
             f"gpu_procs={[(p['name'], p['sm']) for p in procs[:4]]}")
    pw_post("/session/start", {k: v for k, v in session.items() if k != "metrics"})
    return session


def end_session(session: dict, all_metrics: list[dict]) -> None:
    session["end_ts"] = datetime.now(timezone.utc).isoformat()
    session["metrics"] = all_metrics

    # Compute summary stats
    temps  = [m["temp_c"]  for m in all_metrics]
    utils  = [m["gpu_util"] for m in all_metrics]
    vrampcts = [m["vram_pct"] for m in all_metrics]

    summary = {
        "duration_s":    len(all_metrics) * ACTIVE_INTERVAL,
        "temp_max":      max(temps, default=0),
        "temp_avg":      round(sum(temps) / len(temps), 1) if temps else 0,
        "util_avg":      round(sum(utils) / len(utils), 1) if utils else 0,
        "vram_peak_pct": max(vrampcts, default=0),
        "throttle_events": sum(1 for m in all_metrics if m.get("throttled")),
        "total_samples": len(all_metrics),
        "alerts":        session["alerts"],
        "fixes_applied": session["fixes_applied"],
    }
    session["summary"] = summary

    # Save session JSON
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = SESSION_DIR / f"session_{ts_str}_{session['session_id']}.json"
    fname.write_text(json.dumps(session, indent=2))
    log.info(f"SESSION END    id={session['session_id']}  duration={summary['duration_s']:.0f}s  "
             f"max_temp={summary['temp_max']}°C  throttle_events={summary['throttle_events']}")

    pw_post("/session/end", {**{k: v for k, v in session.items() if k != "metrics"}, "summary": summary})
    git_commit_session(fname)


def git_commit_session(session_file: Path) -> None:
    try:
        subprocess.run(["git", "-C", str(SESSION_DIR), "add", session_file.name],
                       capture_output=True)
        msg = f"session: {session_file.stem}"
        subprocess.run(["git", "-C", str(SESSION_DIR), "commit", "-m", msg],
                       capture_output=True)
        log.info(f"Git committed: {session_file.name}")
    except Exception as e:
        log.warning(f"Git commit failed: {e}")

# ── Alert handling ────────────────────────────────────────────────────────────
def check_local_thresholds(metrics: dict, session: dict, low_util_streak: int) -> tuple[list[str], int]:
    """Check thresholds locally, return (alerts_fired, updated_low_util_streak)."""
    alerts = []

    if metrics["temp_c"] >= THRESH_TEMP_WARN:
        alerts.append(f"THERMAL: {metrics['temp_c']}°C >= {THRESH_TEMP_WARN}°C")

    if metrics["vram_pct"] >= THRESH_VRAM_PCT:
        alerts.append(f"VRAM_PRESSURE: {metrics['vram_pct']}% >= {THRESH_VRAM_PCT}%")

    if metrics["throttled"]:
        flags = ",".join(metrics.get("throttle_flags", [])) or f"0x{metrics['throttle']:x}"
        alerts.append(f"THROTTLE: {flags}")

    # Resume-stall detector: nvidia-smi blocking abnormally long means the GPU
    # stalled waking from RTD3 — the actual signature of the desktop freeze.
    if metrics.get("smi_latency_ms", 0) >= THRESH_SMI_LAT * 1000:
        alerts.append(
            f"STALL: nvidia-smi blocked {metrics['smi_latency_ms']:.0f}ms "
            f"(pstate={metrics.get('pstate')} rtd3={metrics.get('runtime_status')}) "
            f"@ {metrics['ts']}"
        )

    # Hang detection: track consecutive low-util samples
    if metrics["gpu_util"] < 5:
        low_util_streak += 1
        hang_threshold = int(THRESH_HANG_SECS / ACTIVE_INTERVAL)
        if low_util_streak == hang_threshold:
            alerts.append(f"HANG_SUSPECTED: GPU util <5% for {THRESH_HANG_SECS}s")
    else:
        low_util_streak = 0

    for alert in alerts:
        if alert not in session["alerts"]:
            session["alerts"].append(alert)
            log.warning(f"ALERT  [{session['session_id']}]  {alert}")

    return alerts, low_util_streak

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("GPU Guardian started")
    log.info(f"PIXEL-WATCH endpoint: {PIXEL_WATCH_URL}")
    log.info(f"Sessions dir: {SESSION_DIR}")

    session      = None
    all_metrics  = []
    low_util_streak = 0
    metric_buf   = []   # buffer metrics, send in batch every 2s
    last_send    = 0
    last_classify = 0  # timestamp of last game re-classification
    RECLASSIFY_INTERVAL = 30  # seconds — re-check game label while session is young

    while True:
        loop_start = time.perf_counter()

        # RTD3 gate: if the dGPU is fully runtime-suspended and we're not already
        # in a session, it cannot be running a game — skip nvidia-smi entirely so
        # we don't wake it. (Polling a suspended GPU defeats RTD3 power saving and
        # can itself trigger the resume-stall micro-hitches.)
        if session is None and gpu_runtime_status() in ("suspended", "suspending"):
            time.sleep(IDLE_INTERVAL)
            continue

        procs = get_nvidia_procs()

        if procs:
            # ── Gaming active ──────────────────────────────────────
            if session is None:
                session = start_session(procs)
                all_metrics = []
                low_util_streak = 0
                metric_buf = []
                last_send = time.time()
                last_classify = time.time()
            elif time.time() - last_classify >= RECLASSIFY_INTERVAL:
                # Re-evaluate game label for first 5 minutes — the actual game
                # process often starts after steam/compositor already grabbed the GPU
                elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(session["start_ts"])).total_seconds()
                if elapsed < 300:
                    new_game = classify_session(procs)
                    if new_game != session["game"]:
                        log.info(f"SESSION RECLASSIFY  id={session['session_id']}  "
                                 f"{session['game']!r} → {new_game!r}")
                        session["game"] = new_game
                        session["all_gpu_procs"] = [{"pid": p["pid"], "name": p["name"], "sm": p["sm"]} for p in procs]
                last_classify = time.time()

            metrics = get_gpu_metrics()
            if metrics:
                all_metrics.append(metrics)
                metric_buf.append(metrics)

                local_alerts, low_util_streak = check_local_thresholds(
                    metrics, session, low_util_streak
                )

                # Send batch to PIXEL-WATCH every 2s
                if time.time() - last_send >= 2.0:
                    pw_post("/session/metrics", {
                        "session_id": session["session_id"],
                        "metrics": metric_buf,
                        "alerts": local_alerts,
                    })
                    metric_buf = []
                    last_send = time.time()

                    # Check for fix commands from PIXEL-WATCH
                    resp = pw_get(f"/session/alerts?session_id={session['session_id']}")
                    if resp and resp.get("fixes"):
                        for fix in resp["fixes"]:
                            output = apply_fix(fix, metrics)
                            session["fixes_applied"].append({"fix": fix, "output": output})
                            log.info(f"Applied fix [{fix}]: {output[:120]}")

            # Loop-level stall guard: the poll loop should take ~ACTIVE_INTERVAL plus
            # a few ms of work. If it ran far longer, *something* froze the whole
            # pipeline (compositor, journalctl, GPU) — record it with a timestamp.
            work_s = time.perf_counter() - loop_start
            if work_s >= THRESH_LOOP_STALL:
                stall = f"LOOP_STALL: poll iteration took {work_s:.1f}s @ {datetime.now(timezone.utc).isoformat()}"
                if stall not in session["alerts"]:
                    session["alerts"].append(stall)
                    log.warning(f"ALERT  [{session['session_id']}]  {stall}")

            time.sleep(ACTIVE_INTERVAL)

        else:
            # ── Idle ───────────────────────────────────────────────
            if session is not None:
                # Flush remaining buffer
                if metric_buf:
                    pw_post("/session/metrics", {
                        "session_id": session["session_id"],
                        "metrics": metric_buf,
                        "alerts": [],
                    })
                end_session(session, all_metrics)
                session = None
                all_metrics = []
                metric_buf = []
                low_util_streak = 0

            time.sleep(IDLE_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Guardian stopped by user")
        sys.exit(0)
