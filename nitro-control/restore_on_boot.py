#!/usr/bin/env python3
"""
nitro-restore — Boot settings restore for Nitro Control
Called by nitro-control-restore.service after linuwu_sense loads.
Reads ~/.config/nitro-control/settings.json and writes all values to sysfs.
"""

import json
import sys
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[nitro-restore] %(asctime)s %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger()

CONFIG_FILE = Path('/etc/nitro-control/settings.json')
USER_CONFIG = Path.home() / '.config' / 'nitro-control' / 'settings.json'
HELPER = '/usr/local/bin/nitro-helper'

DEFAULTS = {
    'profile': 'balanced',
    'battery_limiter': 0,
    'usb_charging': 30,
    'lcd_override': -1,
    'boot_animation_sound': 1,
    'fan_auto': True,
    'fan_cpu': 0,
    'fan_gpu': 0,
}


def write(node, value):
    try:
        result = subprocess.run(
            [HELPER, 'write', node, str(value)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            log.info(f'  {node} = {value}')
            return True
        else:
            log.warning(f'  FAILED {node}: {result.stderr.strip()}')
            return False
    except Exception as e:
        log.error(f'  ERROR {node}: {e}')
        return False


def main():
    # Find config - prefer user config, fall back to system config
    cfg_path = USER_CONFIG if USER_CONFIG.exists() else CONFIG_FILE
    settings = dict(DEFAULTS)

    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text())
            settings.update(data)
            log.info(f'Loaded settings from {cfg_path}')
        except Exception as e:
            log.warning(f'Could not load settings ({e}), using defaults')
    else:
        log.info('No settings file found, applying defaults')

    log.info('Restoring Nitro hardware settings...')

    write('profile', settings['profile'])
    write('battery_limiter', settings['battery_limiter'])
    write('usb_charging', settings['usb_charging'])
    write('lcd_override', settings['lcd_override'])
    write('boot_animation_sound', settings['boot_animation_sound'])

    if settings.get('fan_auto', True):
        write('fan_speed', '0,0')
    else:
        cpu = settings.get('fan_cpu', 0)
        gpu = settings.get('fan_gpu', 0)
        write('fan_speed', f'{cpu},{gpu}')

    log.info('Restore complete.')


if __name__ == '__main__':
    main()
