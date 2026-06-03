#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
#  Nitro Control — Full Installer
#  Acer Nitro ANV15-52 · Ultramarine Linux · CachyOS Kernel
#
#  Usage: bash install.sh
#
#  What this does:
#   1. Installs Python deps (PyQt6, PyQt6-WebEngine)
#   2. Copies app files to /usr/local/lib/nitro-control/
#   3. Installs privileged helper to /usr/local/bin/nitro-helper
#   4. Installs polkit policy
#   5. Installs modprobe config (linuwu_sense nitro_v4=1 + blacklist acer_wmi)
#   6. Installs & enables systemd boot-restore service
#   7. Creates launcher script at /usr/local/bin/nitro-control
#   8. Installs .desktop file for app menu
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
CYN='\033[0;36m'; BLD='\033[1m'; RST='\033[0m'

info()  { echo -e "${CYN}[INFO]${RST}  $*"; }
ok()    { echo -e "${GRN}[ OK ]${RST}  $*"; }
warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
err()   { echo -e "${RED}[ERR ]${RST}  $*"; exit 1; }
step()  { echo -e "\n${BLD}${CYN}━━━ $* ━━━${RST}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLD}"
echo "  ███╗   ██╗██╗████████╗██████╗  ██████╗"
echo "  ████╗  ██║██║╚══██╔══╝██╔══██╗██╔═══██╗"
echo "  ██╔██╗ ██║██║   ██║   ██████╔╝██║   ██║"
echo "  ██║╚██╗██║██║   ██║   ██╔══██╗██║   ██║"
echo "  ██║ ╚████║██║   ██║   ██║  ██║╚██████╔╝"
echo "  ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝"
echo "  CONTROL  ·  ANV15-52  ·  INSTALLER${RST}"
echo ""

# ── Check running as root ────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "Run this installer as root: sudo bash install.sh"
fi

REAL_USER="${SUDO_USER:-$USER}"
info "Installing for user: ${REAL_USER}"

# ── 1. Python deps ───────────────────────────────────────────────────────────
step "Installing Python dependencies"

if command -v dnf &>/dev/null; then
    dnf install -y \
        python3-pyqt6 \
        python3-pyqt6-webengine \
        python3-pyqt6-qt6webengine \
        qt6-qtwebengine \
        polkit \
        2>/dev/null || true

    # Try pip for PyQt6 WebEngine if dnf package not found
    if ! python3 -c "from PyQt6.QtWebEngineWidgets import QWebEngineView" 2>/dev/null; then
        warn "Trying pip for PyQt6-WebEngine..."
        pip3 install PyQt6 PyQt6-WebEngine --break-system-packages 2>/dev/null || \
        pip3 install PyQt6 PyQt6-WebEngine 2>/dev/null || true
    fi
elif command -v pip3 &>/dev/null; then
    pip3 install PyQt6 PyQt6-WebEngine --break-system-packages || \
    pip3 install PyQt6 PyQt6-WebEngine
fi

python3 -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('PyQt6 WebEngine OK')" \
    && ok "PyQt6 WebEngine available" \
    || warn "PyQt6 WebEngine not confirmed — app may need manual package install"

# ── 2. App files ─────────────────────────────────────────────────────────────
step "Installing application files"

APP_LIB=/usr/local/lib/nitro-control
mkdir -p "${APP_LIB}/ui"

cp "${SCRIPT_DIR}/nitro_control.py"    "${APP_LIB}/"
cp "${SCRIPT_DIR}/backend.py"          "${APP_LIB}/"
cp "${SCRIPT_DIR}/restore_on_boot.py"  "${APP_LIB}/"
cp -r "${SCRIPT_DIR}/ui/"              "${APP_LIB}/ui/"

chmod -R 755 "${APP_LIB}"
ok "App files → ${APP_LIB}"

# ── 3. Privileged helper ──────────────────────────────────────────────────────
step "Installing privileged helper"

cp "${SCRIPT_DIR}/privileged_helper.py" /usr/local/bin/nitro-helper
chmod 755 /usr/local/bin/nitro-helper
chown root:root /usr/local/bin/nitro-helper
ok "Helper → /usr/local/bin/nitro-helper"

# ── 4. Polkit policy ─────────────────────────────────────────────────────────
step "Installing polkit policy"

POLKIT_DIR="/usr/share/polkit-1/actions"
cp "${SCRIPT_DIR}/com.nitrocontrol.helper.policy" "${POLKIT_DIR}/"
chmod 644 "${POLKIT_DIR}/com.nitrocontrol.helper.policy"
ok "Polkit policy → ${POLKIT_DIR}"

# Reload polkit
if command -v pkaction &>/dev/null; then
    pkaction --version &>/dev/null && ok "polkit reloaded" || warn "pkaction not responding"
fi

# ── 5. Modprobe config ───────────────────────────────────────────────────────
step "Configuring linuwu_sense module"

cp "${SCRIPT_DIR}/linuwu_sense.conf" /etc/modprobe.d/linuwu_sense.conf
chmod 644 /etc/modprobe.d/linuwu_sense.conf

# Rebuild initramfs so the blacklist takes effect on next boot
if command -v dracut &>/dev/null; then
    info "Rebuilding initramfs with dracut..."
    dracut --force 2>/dev/null && ok "initramfs rebuilt" || warn "dracut failed — run manually"
elif command -v mkinitcpio &>/dev/null; then
    mkinitcpio -P 2>/dev/null && ok "initramfs rebuilt" || warn "mkinitcpio failed"
fi

ok "modprobe config → /etc/modprobe.d/linuwu_sense.conf"

# ── 6. Systemd service ───────────────────────────────────────────────────────
step "Installing systemd boot-restore service"

cp "${SCRIPT_DIR}/nitro-control-restore.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/nitro-control-restore.service

systemctl daemon-reload
systemctl enable nitro-control-restore.service
ok "Service enabled: nitro-control-restore"

# ── 7. Launcher ──────────────────────────────────────────────────────────────
step "Creating launcher"

cat > /usr/local/bin/nitro-control << 'EOF'
#!/usr/bin/env bash
exec python3 /usr/local/lib/nitro-control/nitro_control.py "$@"
EOF
chmod 755 /usr/local/bin/nitro-control
ok "Launcher → /usr/local/bin/nitro-control"

# ── 8. Desktop file ──────────────────────────────────────────────────────────
step "Installing application menu entry"

cp "${SCRIPT_DIR}/nitro-control.desktop" /usr/share/applications/
chmod 644 /usr/share/applications/nitro-control.desktop

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi
ok "Desktop entry → /usr/share/applications/nitro-control.desktop"

# ── 9. Config dir for user ────────────────────────────────────────────────────
step "Setting up user config"
USER_HOME=$(eval echo ~"${REAL_USER}")
CONFIG_DIR="${USER_HOME}/.config/nitro-control"
mkdir -p "${CONFIG_DIR}"
chown -R "${REAL_USER}:${REAL_USER}" "${CONFIG_DIR}"
ok "Config dir → ${CONFIG_DIR}"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLD}${GRN}════════════════════════════════════════════${RST}"
echo -e "${BLD}${GRN}  Nitro Control installed successfully!${RST}"
echo -e "${BLD}${GRN}════════════════════════════════════════════${RST}"
echo ""
echo -e "  Run:    ${CYN}nitro-control${RST}"
echo -e "  Or:     ${CYN}python3 /usr/local/lib/nitro-control/nitro_control.py${RST}"
echo ""
echo -e "  ${YLW}NOTE:${RST} Reboot to apply acer_wmi blacklist & initramfs changes"
echo -e "  ${YLW}NOTE:${RST} Boot restore service will auto-apply your settings"
echo ""
