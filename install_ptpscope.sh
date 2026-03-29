#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# PTPScope Installer — Hub/Spoke GPS PTP Grandmaster
# ─────────────────────────────────────────────────────────────────────────────
set -Eeuo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

step()  { echo -e "\n${CYAN}${BOLD}▸ $1${NC}"; }
ok()    { echo -e "  ${GREEN}✔ $1${NC}"; }
warn()  { echo -e "  ${YELLOW}⚠ $1${NC}"; }
err()   { echo -e "  ${RED}✘ $1${NC}"; }
info()  { echo -e "  $1"; }

INSTALL_ROOT="/opt/ptpscope"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REBOOT_NEEDED=false

# ── Root check ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (sudo)."
    exit 1
fi

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}${BOLD}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║       PTPScope Installer v1.1.0          ║"
echo "  ║     GPS→NTP→PTP Grandmaster Suite        ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Role selection ────────────────────────────────────────────────────────────
echo -e "${BOLD}Select node role:${NC}"
echo "  1) GPS Source  — Raspberry Pi with GPS HAT (reads GPS/PPS, acts as stratum-1 NTP)"
echo "  2) PTP Master  — Machine with hardware PTP NIC (runs ptp4l grandmaster)"
echo "  3) Standalone  — Single machine with GPS HAT + PTP NIC (original behaviour)"
echo ""
read -rp "  Enter choice [1-3]: " ROLE_CHOICE

case "$ROLE_CHOICE" in
    1) NODE_ROLE="gps_source";  ROLE_LABEL="GPS Source" ;;
    2) NODE_ROLE="ptp_master";  ROLE_LABEL="PTP Master" ;;
    3) NODE_ROLE="standalone";  ROLE_LABEL="Standalone" ;;
    *) err "Invalid choice."; exit 1 ;;
esac

info "Installing as: ${BOLD}${ROLE_LABEL}${NC}"

# ── Gather additional info for non-standalone roles ───────────────────────────
NODE_SITE_NAME=""
NODE_SECRET_KEY=""
NODE_HUB_URL=""

if [[ "$NODE_ROLE" != "standalone" ]]; then
    echo ""
    read -rp "  Site name for this node (e.g. gps-pi or ptp-master): " NODE_SITE_NAME
    NODE_SITE_NAME="${NODE_SITE_NAME:-${NODE_ROLE}}"

    read -rp "  Shared secret key (leave blank to generate): " NODE_SECRET_KEY
    if [[ -z "$NODE_SECRET_KEY" ]]; then
        NODE_SECRET_KEY=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 40 || true)
        ok "Generated secret key: ${NODE_SECRET_KEY}"
        warn "Copy this key — you will need it on the other node too."
    fi

    if [[ "$NODE_ROLE" == "gps_source" ]]; then
        read -rp "  PTP Master web UI URL (e.g. http://192.168.1.100:5001): " NODE_HUB_URL
    fi
fi

# ── Check platform ────────────────────────────────────────────────────────────
step "Checking platform"
if [[ -f /proc/device-tree/model ]]; then
    PI_MODEL=$(tr -d '\0' < /proc/device-tree/model)
    ok "Detected: ${PI_MODEL}"
else
    if [[ "$NODE_ROLE" == "gps_source" ]]; then
        warn "GPS Source should run on a Raspberry Pi — some features may not work on other hardware"
    else
        ok "Non-Pi hardware (expected for PTP Master role)"
    fi
    PI_MODEL="Unknown"
fi

ARCH=$(uname -m)
info "Architecture: ${ARCH}"
info "Kernel: $(uname -r)"

# ── Install apt packages ─────────────────────────────────────────────────────
step "Installing system packages"
apt-get update -qq

# Common packages
PACKAGES=(
    chrony
    python3
    python3-venv
    python3-pip
)

# Role-specific packages
if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    PACKAGES+=(gpsd gpsd-clients pps-tools)
fi

if [[ "$NODE_ROLE" == "ptp_master" || "$NODE_ROLE" == "standalone" ]]; then
    PACKAGES+=(linuxptp ethtool)
fi

for pkg in "${PACKAGES[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
        ok "$pkg (already installed)"
    else
        apt-get install -y -qq "$pkg" && ok "$pkg" || warn "Failed to install $pkg"
    fi
done

# ── GPS Source: configure UART, GPSD, PPS ────────────────────────────────────
if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    step "Configuring serial UART for GPS HAT"

    # Determine config file location
    if [[ -f /boot/firmware/config.txt ]]; then
        BOOT_CONFIG="/boot/firmware/config.txt"
        CMDLINE="/boot/firmware/cmdline.txt"
    elif [[ -f /boot/config.txt ]]; then
        BOOT_CONFIG="/boot/config.txt"
        CMDLINE="/boot/cmdline.txt"
    else
        warn "Cannot find boot config — skipping UART configuration"
        BOOT_CONFIG=""
        CMDLINE=""
    fi

    if [[ -n "$BOOT_CONFIG" ]]; then
        if grep -q "^enable_uart=1" "$BOOT_CONFIG"; then
            ok "UART already enabled"
        else
            echo "enable_uart=1" >> "$BOOT_CONFIG"
            ok "UART enabled in ${BOOT_CONFIG}"
            REBOOT_NEEDED=true
        fi

        if grep -q "^dtoverlay=pps-gpio" "$BOOT_CONFIG"; then
            ok "PPS GPIO overlay already configured"
        else
            echo "dtoverlay=pps-gpio,gpiopin=4" >> "$BOOT_CONFIG"
            ok "PPS GPIO overlay added (GPIO 4)"
            REBOOT_NEEDED=true
        fi

        if [[ -n "$CMDLINE" && -f "$CMDLINE" ]]; then
            if grep -q "console=serial0" "$CMDLINE"; then
                sed -i 's/console=serial0,[0-9]* //g' "$CMDLINE"
                ok "Serial console disabled (was conflicting with GPS)"
                REBOOT_NEEDED=true
            else
                ok "Serial console already disabled"
            fi
        fi
    fi

    step "Configuring GPSD"
    cat > /etc/default/gpsd <<'GPSDCONF'
# PTPScope — GPSD configuration
DEVICES="/dev/serial0"
GPSD_OPTIONS="-n"
GPSD_SOCKET="/var/run/gpsd.sock"
START_DAEMON="true"
USBAUTO="false"
GPSDCONF
    ok "GPSD configured for /dev/serial0"
    systemctl enable gpsd 2>/dev/null && ok "GPSD service enabled" || warn "Could not enable GPSD"
fi

# ── Configure Chrony ──────────────────────────────────────────────────────────
step "Configuring Chrony"

CHRONY_CONF="/etc/chrony/chrony.conf"
if [[ ! -f "$CHRONY_CONF" ]]; then
    CHRONY_CONF="/etc/chrony.conf"
fi

if [[ -f "$CHRONY_CONF" ]]; then
    cp "$CHRONY_CONF" "${CHRONY_CONF}.ptpscope-backup"
    ok "Backed up ${CHRONY_CONF}"

    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
        # GPS Source: use GPS/PPS refclocks, serve NTP to local network
        if grep -q "refclock SHM 0" "$CHRONY_CONF"; then
            ok "GPS SHM refclock already configured"
        else
            cat >> "$CHRONY_CONF" <<'CHRONYAPPEND'

# ── PTPScope GPS + PPS configuration ────────────────────────────────────────
# GPS via shared memory from GPSD
refclock SHM 0 refid GPS precision 1e-1 offset 0.0 delay 0.2 noselect
# PPS from kernel PPS driver — locked to GPS for coarse time
refclock PPS /dev/pps0 refid PPS precision 1e-7 lock GPS
# Allow NTP clients on local network
allow 192.168.0.0/16
allow 10.0.0.0/8
allow 172.16.0.0/12
CHRONYAPPEND
            ok "GPS SHM + PPS refclocks and NTP server allow rules added"
        fi
    fi

    if [[ "$NODE_ROLE" == "ptp_master" ]]; then
        # PTP Master: sync from GPS Source NTP (user will configure hub_url later via web UI)
        if grep -q "# PTPScope PTP Master" "$CHRONY_CONF"; then
            ok "PTP Master chrony config already present"
        else
            cat >> "$CHRONY_CONF" <<'CHRONYAPPEND'

# ── PTPScope PTP Master configuration ───────────────────────────────────────
# Primary time source is the GPS Source node's NTP server.
# Update the server address below to match your GPS Source Pi's IP.
# server 192.168.1.x iburst prefer
# makestep 1 3
CHRONYAPPEND
            ok "PTP Master chrony stanza added (edit ${CHRONY_CONF} to set GPS Source IP)"
        fi
    fi

    systemctl restart chrony 2>/dev/null && ok "Chrony restarted" || warn "Could not restart chrony"
else
    warn "Chrony config not found — please configure manually"
fi

# ── Create install directory ──────────────────────────────────────────────────
step "Setting up PTPScope"
mkdir -p "${INSTALL_ROOT}/static"
ok "Created ${INSTALL_ROOT}"

# ── Python virtual environment ────────────────────────────────────────────────
step "Creating Python virtual environment"
if [[ -d "${INSTALL_ROOT}/venv" ]]; then
    ok "Virtual environment already exists"
else
    python3 -m venv "${INSTALL_ROOT}/venv"
    ok "Virtual environment created"
fi

"${INSTALL_ROOT}/venv/bin/pip" install --upgrade pip -q
ok "pip upgraded"

PIP_PKGS="flask waitress"
if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    PIP_PKGS="$PIP_PKGS pyserial"
fi
"${INSTALL_ROOT}/venv/bin/pip" install $PIP_PKGS -q
ok "Python packages installed (${PIP_PKGS})"

# ── Copy application ──────────────────────────────────────────────────────────
step "Installing PTPScope application"
if [[ -f "${SCRIPT_DIR}/ptpscope.py" ]]; then
    cp "${SCRIPT_DIR}/ptpscope.py" "${INSTALL_ROOT}/ptpscope.py"
    chmod 644 "${INSTALL_ROOT}/ptpscope.py"
    ok "ptpscope.py installed"
else
    err "ptpscope.py not found in ${SCRIPT_DIR}"
    exit 1
fi

if [[ -f "${SCRIPT_DIR}/static/ptpscope_icon.png" ]]; then
    cp "${SCRIPT_DIR}/static/ptpscope_icon.png" "${INSTALL_ROOT}/static/"
    ok "Icon copied"
fi

# ── Write initial config with node role ───────────────────────────────────────
step "Writing node configuration"
CONFIG_FILE="${INSTALL_ROOT}/ptpscope_config.json"

# Only create if it doesn't exist yet (don't overwrite user's existing config)
if [[ ! -f "$CONFIG_FILE" ]]; then
    cat > "$CONFIG_FILE" <<EOF
{
  "node": {
    "role": "${NODE_ROLE}",
    "site_name": "${NODE_SITE_NAME}",
    "secret_key": "${NODE_SECRET_KEY}",
    "hub_url": "${NODE_HUB_URL}"
  },
  "web_port": 5001,
  "bind_address": "0.0.0.0"
}
EOF
    chmod 600 "$CONFIG_FILE"
    ok "Config written to ${CONFIG_FILE}"
else
    ok "Config already exists — not overwritten. Edit via the web UI."
fi

# ── PTP Master: check hardware timestamping ───────────────────────────────────
if [[ "$NODE_ROLE" == "ptp_master" || "$NODE_ROLE" == "standalone" ]]; then
    step "Checking network hardware timestamping"
    DEFAULT_IFACE=$(ip route show default 2>/dev/null | head -1 | awk '{print $5}' || echo "eth0")
    if [[ -z "$DEFAULT_IFACE" ]]; then
        DEFAULT_IFACE="eth0"
    fi
    # Intel/Broadcom NICs report "hardware-transmit"; Mellanox ConnectX cards
    # report "SOF_TIMESTAMPING_TX_HARDWARE" — check both patterns.
    ETHTOOL_OUT=$(ethtool -T "$DEFAULT_IFACE" 2>/dev/null || true)
    if echo "$ETHTOOL_OUT" | grep -qE "hardware-transmit|SOF_TIMESTAMPING_TX_HARDWARE"; then
        ok "${DEFAULT_IFACE} supports hardware timestamping"
        TS_MODE="hardware"
    else
        warn "${DEFAULT_IFACE} does not support hardware timestamping — using software mode"
        TS_MODE="software"
        info "PTP accuracy will be reduced (~10-100 µs vs ~100 ns with hardware timestamping)"
    fi
fi

# ── GPS Source: verify PPS ────────────────────────────────────────────────────
if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    step "Checking PPS device"
    if [[ -e /dev/pps0 ]]; then
        ok "/dev/pps0 exists — PPS ready"
        if command -v ppstest &>/dev/null; then
            timeout 3 ppstest /dev/pps0 2>&1 | head -3 || true
        fi
    else
        if $REBOOT_NEEDED; then
            info "/dev/pps0 not yet available — will appear after reboot"
        else
            warn "/dev/pps0 not found — PPS may not be connected or overlay not loaded"
        fi
    fi
fi

# ── Create systemd service ────────────────────────────────────────────────────
step "Creating systemd service"
cat > /etc/systemd/system/ptpscope.service <<EOF
[Unit]
Description=PTPScope — ${ROLE_LABEL}
After=network-online.target chrony.service
Wants=network-online.target
EOF

if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    cat >> /etc/systemd/system/ptpscope.service <<'EOF'
After=network-online.target gpsd.service chrony.service
EOF
fi

cat >> /etc/systemd/system/ptpscope.service <<EOF

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_ROOT}
ExecStart=${INSTALL_ROOT}/venv/bin/python ${INSTALL_ROOT}/ptpscope.py
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW CAP_SYS_TIME
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ptpscope.service
ok "ptpscope.service created and enabled"

# ── Start service ─────────────────────────────────────────────────────────────
step "Starting PTPScope"
if $REBOOT_NEEDED; then
    warn "Reboot required for UART/PPS changes — service will start after reboot"
else
    systemctl start ptpscope.service
    sleep 2
    if systemctl is-active --quiet ptpscope.service; then
        ok "PTPScope is running"
    else
        warn "PTPScope may have failed to start — check: journalctl -u ptpscope -f"
    fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║              PTPScope Installation Complete              ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "<your-ip>")
if [[ -z "$IP_ADDR" ]]; then IP_ADDR="<your-ip>"; fi

echo -e "  ${BOLD}Role:${NC}          ${ROLE_LABEL}"
echo -e "  ${BOLD}Web UI:${NC}        http://${IP_ADDR}:5001"
echo -e "  ${BOLD}Install dir:${NC}   ${INSTALL_ROOT}"
echo -e "  ${BOLD}Config:${NC}        ${INSTALL_ROOT}/ptpscope_config.json"
echo ""

if [[ "$NODE_ROLE" == "gps_source" ]]; then
    echo -e "  ${BOLD}Next steps:${NC}"
    echo -e "    1. On the PTP Master, install PTPScope with role 'PTP Master'"
    echo -e "    2. Use the same secret key on both machines"
    echo -e "    3. Set the GPS Source URL in the PTP Master web UI: http://${IP_ADDR}:5001"
    echo -e "    4. On the PTP Master, edit chrony.conf to use this node as NTP server: ${IP_ADDR}"
    echo ""
fi

if [[ "$NODE_ROLE" == "ptp_master" ]]; then
    echo -e "  ${BOLD}Next steps:${NC}"
    echo -e "    1. Edit /etc/chrony/chrony.conf — add: server <gps-pi-ip> iburst prefer"
    echo -e "    2. sudo systemctl restart chrony"
    echo -e "    3. In the PTPScope web UI → Configuration → Node, set the GPS Source secret key"
    echo ""
    if [[ -n "${TS_MODE:-}" ]]; then
        echo -e "  ${BOLD}Timestamping:${NC}  ${TS_MODE}"
    fi
fi

echo -e "  ${BOLD}Service commands:${NC}"
echo -e "    sudo systemctl status ptpscope"
echo -e "    sudo systemctl restart ptpscope"
echo -e "    sudo journalctl -u ptpscope -f"
echo ""

if $REBOOT_NEEDED; then
    echo -e "  ${YELLOW}${BOLD}⚠  REBOOT REQUIRED${NC}"
    echo -e "  ${YELLOW}Serial UART and/or PPS GPIO changes need a reboot to take effect.${NC}"
    echo -e "  ${YELLOW}Run: sudo reboot${NC}"
    echo ""
fi

echo -e "  ${GREEN}${BOLD}PTPScope is ready.${NC}"
echo ""
