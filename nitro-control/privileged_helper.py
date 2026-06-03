#!/usr/bin/env python3
"""
nitro-helper — Privileged sysfs helper for Nitro Control
Run via: pkexec /usr/local/bin/nitro-helper write <node> <value>

Installed by install.sh to /usr/local/bin/nitro-helper
Authorized by polkit policy com.nitrocontrol.helper.policy
"""

import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[nitro-helper] %(message)s')
log = logging.getLogger()

NITRO = Path('/sys/devices/platform/acer-wmi/nitro_sense')
PROFILE = Path('/sys/devices/platform/acer-wmi/platform-profile/platform-profile-0/profile')

# Strict whitelist — only these nodes can be written
ALLOWED_NODES = {
    'fan_speed':            NITRO / 'fan_speed',
    'battery_limiter':      NITRO / 'battery_limiter',
    'usb_charging':         NITRO / 'usb_charging',
    'lcd_override':         NITRO / 'lcd_override',
    'boot_animation_sound': NITRO / 'boot_animation_sound',
    'battery_calibration':  NITRO / 'battery_calibration',
    'profile':              PROFILE,
}

# Value validators
def validate_value(node: str, value: str) -> bool:
    if node == 'fan_speed':
        parts = value.split(',')
        if len(parts) != 2:
            return False
        try:
            cpu, gpu = int(parts[0]), int(parts[1])
            return 0 <= cpu <= 5000 and 0 <= gpu <= 5000
        except ValueError:
            return False
    if node == 'battery_limiter':
        return value in ('0', '1')
    if node == 'usb_charging':
        try:
            v = int(value)
            return 0 <= v <= 120
        except ValueError:
            return False
    if node == 'lcd_override':
        return value in ('-1', '0', '1')
    if node == 'boot_animation_sound':
        return value in ('0', '1')
    if node == 'battery_calibration':
        return value == '1'
    if node == 'profile':
        return value in ('low-power', 'quiet', 'balanced', 'balanced-performance', 'performance')
    return False


def cmd_write(node: str, value: str):
    if node not in ALLOWED_NODES:
        log.error(f'Rejected: unknown node "{node}"')
        sys.exit(2)
    if not validate_value(node, value):
        log.error(f'Rejected: invalid value "{value}" for node "{node}"')
        sys.exit(3)
    target = ALLOWED_NODES[node]
    if not target.exists():
        log.error(f'Sysfs path not found: {target} — is linuwu_sense loaded?')
        sys.exit(4)
    try:
        target.write_text(value)
        log.info(f'OK: {node} = {value}')
    except OSError as e:
        log.error(f'Write failed: {e}')
        sys.exit(5)


def cmd_read(node: str):
    if node not in ALLOWED_NODES:
        log.error(f'Rejected: unknown node "{node}"')
        sys.exit(2)
    target = ALLOWED_NODES[node]
    try:
        print(target.read_text().strip())
    except OSError as e:
        log.error(f'Read failed: {e}')
        sys.exit(5)


def main():
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} write <node> <value>', file=sys.stderr)
        print(f'       {sys.argv[0]} read <node>', file=sys.stderr)
        print(f'Allowed nodes: {", ".join(ALLOWED_NODES.keys())}', file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'write':
        if len(sys.argv) < 4:
            print('write requires <node> and <value>', file=sys.stderr)
            sys.exit(1)
        cmd_write(sys.argv[2], sys.argv[3])

    elif command == 'read':
        cmd_read(sys.argv[2])

    else:
        log.error(f'Unknown command: {command}')
        sys.exit(1)


if __name__ == '__main__':
    main()
