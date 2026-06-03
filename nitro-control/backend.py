#!/usr/bin/env python3
"""
NitroBackend — QObject exposed to JS via QWebChannel
Handles all sysfs I/O, privileged writes via polkit helper,
settings persistence, and telemetry collection.
"""

import json
import logging
import subprocess
import os
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

log = logging.getLogger('nitro-backend')

# ── Sysfs paths ────────────────────────────────────────────────────────────────
NITRO = Path('/sys/devices/platform/acer-wmi/nitro_sense')
HWMON = Path('/sys/devices/platform/acer-wmi/hwmon/hwmon4')
PROFILE_PATH = Path('/sys/devices/platform/acer-wmi/platform-profile/platform-profile-0/profile')
PROFILE_CHOICES = Path('/sys/devices/platform/acer-wmi/platform-profile/platform-profile-0/choices')

# Privileged helper path (installed by install.sh)
HELPER = '/usr/local/bin/nitro-helper'
CONFIG_DIR = Path.home() / '.config' / 'nitro-control'
CONFIG_FILE = CONFIG_DIR / 'settings.json'

DEFAULT_SETTINGS = {
    'profile': 'balanced',
    'battery_limiter': 0,
    'usb_charging': 30,
    'lcd_override': -1,
    'boot_animation_sound': 1,
    'fan_auto': True,
    'fan_cpu': 0,
    'fan_gpu': 0,
    'gpu_power_limit': 75,
    'charge_limit_pct': 100,
    'scx_gaming': True,
}


def _sysfs_read(path: Path) -> str | None:
    """Read a sysfs file, return stripped string or None on error."""
    try:
        return path.read_text().strip()
    except Exception as e:
        log.warning(f'sysfs read {path}: {e}')
        return None


def _privileged_write(node: str, value: str) -> bool:
    """
    Write to a privileged sysfs path via the polkit helper.
    Equivalent to: pkexec nitro-helper write <node> <value>
    """
    if os.path.exists(HELPER):
        try:
            result = subprocess.run(
                ['pkexec', HELPER, 'write', node, str(value)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                log.info(f'[WRITE] {node} = {value}')
                return True
            else:
                log.error(f'Helper failed: {result.stderr}')
                return False
        except subprocess.TimeoutExpired:
            log.error('pkexec timed out')
            return False
        except FileNotFoundError:
            log.warning('pkexec not found, trying direct write')

    # Fallback: direct write (only works if running as root or file is writable)
    node_map = {
        'fan_speed': NITRO / 'fan_speed',
        'battery_limiter': NITRO / 'battery_limiter',
        'usb_charging': NITRO / 'usb_charging',
        'lcd_override': NITRO / 'lcd_override',
        'boot_animation_sound': NITRO / 'boot_animation_sound',
        'battery_calibration': NITRO / 'battery_calibration',
        'profile': PROFILE_PATH,
    }
    target = node_map.get(node)
    if target:
        try:
            target.write_text(str(value))
            log.info(f'[DIRECT] {node} = {value}')
            return True
        except PermissionError:
            log.error(f'Permission denied writing {target}. Install helper with install.sh')
            return False
    log.error(f'Unknown sysfs node: {node}')
    return False


class NitroBackend(QObject):
    """Exposed to JavaScript via QWebChannel as window.backend"""

    # Signals pushed to JS
    logMessage = pyqtSignal(str, str)      # message, level
    settingsChanged = pyqtSignal(str)       # JSON string of changed settings

    def __init__(self, parent=None):
        super().__init__(parent)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.settings = self._load_settings()
        log.info('NitroBackend ready')

    # ── Settings persistence ───────────────────────────────────────────────────

    def _load_settings(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                merged = {**DEFAULT_SETTINGS, **data}
                log.info(f'Settings loaded from {CONFIG_FILE}')
                return merged
            except Exception as e:
                log.warning(f'Settings load error: {e}, using defaults')
        return dict(DEFAULT_SETTINGS)

    def _save_settings(self):
        try:
            CONFIG_FILE.write_text(json.dumps(self.settings, indent=2))
        except Exception as e:
            log.error(f'Settings save error: {e}')

    # ── JS-callable slots ──────────────────────────────────────────────────────

    @pyqtSlot(result=str)
    def get_telemetry(self) -> str:
        """Return JSON with live hwmon data"""
        def millideg(val):
            try:
                return round(int(val) / 1000, 1) if val else None
            except (ValueError, TypeError):
                return None

        cpu_temp = millideg(_sysfs_read(HWMON / 'temp1_input'))
        gpu_temp = millideg(_sysfs_read(HWMON / 'temp2_input'))
        sys_temp = millideg(_sysfs_read(HWMON / 'temp3_input'))
        fan1 = _sysfs_read(HWMON / 'fan1_input')
        fan2 = _sysfs_read(HWMON / 'fan2_input')

        data = {
            'cpu_temp': cpu_temp,
            'gpu_temp': gpu_temp,
            'sys_temp': sys_temp,
            'fan1_rpm': int(fan1) if fan1 else 0,
            'fan2_rpm': int(fan2) if fan2 else 0,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
        }
        return json.dumps(data)

    @pyqtSlot(result=str)
    def get_all_settings(self) -> str:
        """Return full settings JSON for UI init"""
        # Read live values where possible
        bl = _sysfs_read(NITRO / 'battery_limiter')
        usb = _sysfs_read(NITRO / 'usb_charging')
        lcd = _sysfs_read(NITRO / 'lcd_override')
        bas = _sysfs_read(NITRO / 'boot_animation_sound')
        fan = _sysfs_read(NITRO / 'fan_speed')

        if bl is not None:
            self.settings['battery_limiter'] = int(bl)
        if usb is not None:
            self.settings['usb_charging'] = int(usb)
        if lcd is not None:
            self.settings['lcd_override'] = int(lcd)
        if bas is not None:
            self.settings['boot_animation_sound'] = int(bas)
        if fan is not None:
            parts = fan.split(',')
            if len(parts) == 2:
                self.settings['fan_auto'] = (parts[0] == '0' and parts[1] == '0')

        return json.dumps(self.settings)

    @pyqtSlot(str, result=bool)
    def set_profile(self, profile: str) -> bool:
        """Write power profile to platform-profile sysfs"""
        valid = ['low-power', 'quiet', 'balanced', 'balanced-performance', 'performance']
        if profile not in valid:
            log.error(f'Invalid profile: {profile}')
            return False
        ok = _privileged_write('profile', profile)
        if ok:
            self.settings['profile'] = profile
            self._save_settings()
            self.logMessage.emit(f'Profile → {profile}', 'ok')
        return ok

    @pyqtSlot(int, result=bool)
    def set_battery_limiter(self, value: int) -> bool:
        ok = _privileged_write('battery_limiter', str(value))
        if ok:
            self.settings['battery_limiter'] = value
            self._save_settings()
            self.logMessage.emit(f'Battery limiter → {value}', 'ok')
        return ok

    @pyqtSlot(int, result=bool)
    def set_usb_charging(self, minutes: int) -> bool:
        ok = _privileged_write('usb_charging', str(minutes))
        if ok:
            self.settings['usb_charging'] = minutes
            self._save_settings()
            self.logMessage.emit(f'USB charging sleep timeout → {minutes}min', 'ok')
        return ok

    @pyqtSlot(int, result=bool)
    def set_lcd_override(self, value: int) -> bool:
        ok = _privileged_write('lcd_override', str(value))
        if ok:
            self.settings['lcd_override'] = value
            self._save_settings()
            self.logMessage.emit(f'LCD overdrive → {value}', 'ok')
        return ok

    @pyqtSlot(int, result=bool)
    def set_boot_animation(self, value: int) -> bool:
        ok = _privileged_write('boot_animation_sound', str(value))
        if ok:
            self.settings['boot_animation_sound'] = value
            self._save_settings()
        return ok

    @pyqtSlot(bool, result=bool)
    def set_fan_auto(self, auto: bool) -> bool:
        value = '0,0' if auto else f'{self.settings["fan_cpu"]},{self.settings["fan_gpu"]}'
        ok = _privileged_write('fan_speed', value)
        if ok:
            self.settings['fan_auto'] = auto
            self._save_settings()
            mode = 'AUTO (EC controlled)' if auto else 'MANUAL'
            self.logMessage.emit(f'Fan mode → {mode}', 'ok')
        return ok

    @pyqtSlot(int, int, result=bool)
    def set_fan_manual(self, cpu_rpm: int, gpu_rpm: int) -> bool:
        value = f'{cpu_rpm},{gpu_rpm}'
        ok = _privileged_write('fan_speed', value)
        if ok:
            self.settings['fan_cpu'] = cpu_rpm
            self.settings['fan_gpu'] = gpu_rpm
            self.settings['fan_auto'] = False
            self._save_settings()
            self.logMessage.emit(f'Fan manual → CPU:{cpu_rpm} GPU:{gpu_rpm} RPM', 'ok')
        return ok

    @pyqtSlot(result=bool)
    def trigger_battery_calibration(self) -> bool:
        ok = _privileged_write('battery_calibration', '1')
        if ok:
            self.logMessage.emit('Battery calibration triggered', 'warn')
        return ok

    @pyqtSlot(result=str)
    def get_gpu_info(self) -> str:
        """nvidia-smi query for GPU status"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=temperature.gpu,power.draw,power.limit,utilization.gpu,clocks.current.graphics',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 5:
                    return json.dumps({
                        'temp': float(parts[0]),
                        'power_draw': float(parts[1]),
                        'power_limit': float(parts[2]),
                        'utilization': float(parts[3]),
                        'clock_mhz': float(parts[4]),
                    })
        except Exception as e:
            log.warning(f'nvidia-smi failed: {e}')
        return json.dumps({})

    @pyqtSlot(result=str)
    def get_profile_choices(self) -> str:
        choices = _sysfs_read(PROFILE_CHOICES)
        if choices:
            return json.dumps(choices.split())
        return json.dumps(['low-power', 'quiet', 'balanced', 'balanced-performance', 'performance'])

    @pyqtSlot(result=bool)
    def restore_all_settings(self) -> bool:
        """Restore all saved settings to hardware — called on boot by systemd"""
        log.info('Restoring settings to hardware...')
        ok = True
        ok &= _privileged_write('profile', self.settings.get('profile', 'balanced'))
        ok &= _privileged_write('battery_limiter', str(self.settings.get('battery_limiter', 0)))
        ok &= _privileged_write('usb_charging', str(self.settings.get('usb_charging', 30)))
        ok &= _privileged_write('lcd_override', str(self.settings.get('lcd_override', -1)))
        ok &= _privileged_write('boot_animation_sound', str(self.settings.get('boot_animation_sound', 1)))
        fan_auto = self.settings.get('fan_auto', True)
        fan_val = '0,0' if fan_auto else f'{self.settings.get("fan_cpu",0)},{self.settings.get("fan_gpu",0)}'
        ok &= _privileged_write('fan_speed', fan_val)
        log.info(f'Settings restore complete (ok={ok})')
        return ok
