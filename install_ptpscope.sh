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
echo "  ║       PTPScope Installer v1.3.5          ║"
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
GPS_SOURCE_IP=""

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

    if [[ "$NODE_ROLE" == "ptp_master" ]]; then
        echo ""
        read -rp "  GPS Source Pi IP address (for NTP sync, e.g. 192.168.1.50): " GPS_SOURCE_IP
        GPS_SOURCE_IP="${GPS_SOURCE_IP:-}"
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

# Role-specific packages — GPS nodes need pps-tools (but NOT gpsd, PTPScope
# reads the serial port directly and writes NTP SHM itself)
if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
    PACKAGES+=(pps-tools)
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

# ── GPS Source: configure UART, PPS, disable GPSD ────────────────────────────
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

    # PTPScope reads the GPS serial port directly and writes to NTP SHM
    # itself, so GPSD must be disabled to avoid port conflicts.
    step "Disabling GPSD (PTPScope handles GPS directly)"
    systemctl stop gpsd gpsd.socket 2>/dev/null || true
    systemctl disable gpsd gpsd.socket 2>/dev/null || true
    systemctl mask gpsd gpsd.socket 2>/dev/null || true
    ok "GPSD disabled (PTPScope writes NTP SHM directly)"
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

    # ── Write chrony config to conf.d (not chrony.conf) ──────────────────
    # Debian/Ubuntu chrony has a "confdir /etc/chrony/conf.d" directive.
    # Anything appended to chrony.conf AFTER confdir is silently ignored.
    # Writing to conf.d ensures our config is always loaded.
    CHRONY_CONF_DIR="$(dirname "$CHRONY_CONF")/conf.d"
    mkdir -p "$CHRONY_CONF_DIR"

    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
        cat > "${CHRONY_CONF_DIR}/ptpscope.conf" <<'CHRONYCONF'
# ── PTPScope GPS + PPS configuration ────────────────────────────────────────
# GPS via shared memory — written by PTPScope directly (not GPSD)
refclock SHM 0 refid GPS precision 1e-1 offset 0.5 delay 0.2
# PPS from kernel PPS driver — locked to GPS for coarse time
refclock PPS /dev/pps0 refid PPS precision 1e-7 lock GPS prefer
# Allow NTP clients on local network
allow 192.168.0.0/16
allow 10.0.0.0/8
allow 172.16.0.0/12
CHRONYCONF
        ok "GPS SHM + PPS refclocks written to ${CHRONY_CONF_DIR}/ptpscope.conf"
    fi

    if [[ "$NODE_ROLE" == "ptp_master" ]]; then
        if [[ -n "$GPS_SOURCE_IP" ]]; then
            cat > "${CHRONY_CONF_DIR}/ptpscope.conf" <<EOF
# ── PTPScope PTP Master configuration ───────────────────────────────────────
# Primary time source is the GPS Source node's NTP server
server ${GPS_SOURCE_IP} iburst prefer
makestep 1 3
EOF
            ok "Chrony configured to sync from GPS Source at ${GPS_SOURCE_IP}"
        else
            cat > "${CHRONY_CONF_DIR}/ptpscope.conf" <<'CHRONYCONF'
# ── PTPScope PTP Master configuration ───────────────────────────────────────
# Configure the GPS Source IP via the web UI → Settings → Chrony
makestep 1 3
CHRONYCONF
            ok "PTP Master chrony placeholder created — set GPS Source IP in the web UI"
        fi
    fi

    # Clean up any old managed block from chrony.conf (from pre-1.3.4 installs)
    if grep -q "PTPScope GPS + PPS\|PTPScope PTP Master\|PTPScope managed block" "$CHRONY_CONF" 2>/dev/null; then
        sed -i '/# ── PTPScope/,/^$/d' "$CHRONY_CONF"
        sed -i '/# ── PTPScope managed block/,/# ── PTPScope managed block END/d' "$CHRONY_CONF"
        # Also remove any stray refclock/allow lines we previously appended
        sed -i '/^refclock SHM 0/d; /^refclock PPS.*lock GPS/d' "$CHRONY_CONF"
        ok "Cleaned up old PTPScope config from chrony.conf (migrated to conf.d)"
    fi

    # ── Chrony SHM access: disable seccomp filter ────────────────────────
    # Chrony's -F 1 flag (set in /etc/default/chrony on Debian) enables
    # seccomp filtering which prevents reading root-owned SHM segments.
    # Even running chrony as root doesn't help because -F forces privilege
    # drop. Disable it so chrony can read PTPScope's NTP SHM.
    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
        CHRONY_DEFAULT="/etc/default/chrony"
        if [[ -f "$CHRONY_DEFAULT" ]] && grep -q "\-F" "$CHRONY_DEFAULT"; then
            sed -i 's/DAEMON_OPTS=".*-F[^"]*"/DAEMON_OPTS=""/' "$CHRONY_DEFAULT"
            ok "Disabled chrony seccomp filter (-F) for SHM access"
        fi

        # Also set up a systemd drop-in to run chrony as root for SHM access
        CHRONY_DROPIN_DIR=""
        if [[ -f /usr/lib/systemd/system/chrony.service ]]; then
            CHRONY_DROPIN_DIR="/etc/systemd/system/chrony.service.d"
        elif [[ -f /usr/lib/systemd/system/chronyd.service ]]; then
            CHRONY_DROPIN_DIR="/etc/systemd/system/chronyd.service.d"
        fi
        if [[ -n "$CHRONY_DROPIN_DIR" ]]; then
            mkdir -p "$CHRONY_DROPIN_DIR"
            cat > "${CHRONY_DROPIN_DIR}/ptpscope.conf" <<'CHRONYDROP'
[Service]
User=root
Group=root
CHRONYDROP
            ok "Chrony configured to run as root (for SHM access)"
        fi

        systemctl daemon-reload
    fi

    # ── PPS device permissions ───────────────────────────────────────────
    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
        echo 'SUBSYSTEM=="pps", MODE="0664", GROUP="_chrony"' > /etc/udev/rules.d/99-pps-chrony.rules
        udevadm control --reload-rules 2>/dev/null || true
        if [[ -e /dev/pps0 ]]; then
            chmod 664 /dev/pps0
            chgrp _chrony /dev/pps0 2>/dev/null || true
        fi
        ok "PPS device permissions set for chrony access"
    fi

    # ── Restart chrony ───────────────────────────────────────────────────
    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]] && [[ ! -e /dev/pps0 ]]; then
        info "Chrony restart deferred — /dev/pps0 not available until reboot"
    else
        # Try both service names (chrony vs chronyd)
        if systemctl restart chrony 2>/dev/null; then
            ok "Chrony restarted"
        elif systemctl restart chronyd 2>/dev/null; then
            ok "Chrony restarted (chronyd)"
        else
            warn "Could not restart chrony — try: sudo systemctl restart chrony"
        fi
    fi
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

# ── Fetch latest ptpscope.py from GitHub (fall back to local copy) ────────────
step "Installing PTPScope application"
GH_RAW_URL="https://raw.githubusercontent.com/itconor/PtPscope/main/ptpscope.py"
FETCHED=false

if command -v curl &>/dev/null; then
    if curl -fsSL --connect-timeout 10 --max-time 60 -o /tmp/ptpscope_latest.py "$GH_RAW_URL" 2>/dev/null; then
        # Sanity-check: must contain BUILD string
        if grep -q "PTPScope-" /tmp/ptpscope_latest.py; then
            GH_VER=$(grep -oP 'PTPScope-\K[0-9]+\.[0-9]+\.[0-9]+' /tmp/ptpscope_latest.py | head -1)
            cp /tmp/ptpscope_latest.py "${INSTALL_ROOT}/ptpscope.py"
            chmod 644 "${INSTALL_ROOT}/ptpscope.py"
            ok "ptpscope.py ${GH_VER} downloaded from GitHub (latest)"
            FETCHED=true
        else
            warn "Downloaded file doesn't look like PTPScope — using local copy"
        fi
        rm -f /tmp/ptpscope_latest.py
    else
        warn "Could not reach GitHub — using local copy"
    fi
elif command -v wget &>/dev/null; then
    if wget -q --timeout=10 -O /tmp/ptpscope_latest.py "$GH_RAW_URL" 2>/dev/null; then
        if grep -q "PTPScope-" /tmp/ptpscope_latest.py; then
            GH_VER=$(grep -oP 'PTPScope-\K[0-9]+\.[0-9]+\.[0-9]+' /tmp/ptpscope_latest.py | head -1)
            cp /tmp/ptpscope_latest.py "${INSTALL_ROOT}/ptpscope.py"
            chmod 644 "${INSTALL_ROOT}/ptpscope.py"
            ok "ptpscope.py ${GH_VER} downloaded from GitHub (latest)"
            FETCHED=true
        else
            warn "Downloaded file doesn't look like PTPScope — using local copy"
        fi
        rm -f /tmp/ptpscope_latest.py
    else
        warn "Could not reach GitHub — using local copy"
    fi
else
    info "Neither curl nor wget found — using local copy"
fi

if ! $FETCHED; then
    if [[ -f "${SCRIPT_DIR}/ptpscope.py" ]]; then
        cp "${SCRIPT_DIR}/ptpscope.py" "${INSTALL_ROOT}/ptpscope.py"
        chmod 644 "${INSTALL_ROOT}/ptpscope.py"
        LOCAL_VER=$(grep -oP 'PTPScope-\K[0-9]+\.[0-9]+\.[0-9]+' "${INSTALL_ROOT}/ptpscope.py" | head -1)
        ok "ptpscope.py ${LOCAL_VER} installed from local copy"
    else
        err "ptpscope.py not found in ${SCRIPT_DIR} and GitHub download failed"
        exit 1
    fi
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
    # GPS/PPS refclocks only for nodes with GPS hardware
    if [[ "$NODE_ROLE" == "gps_source" || "$NODE_ROLE" == "standalone" ]]; then
        GPS_REFCLOCK="true"
        PPS_REFCLOCK="true"
    else
        GPS_REFCLOCK="false"
        PPS_REFCLOCK="false"
    fi

    cat > "$CONFIG_FILE" <<EOF
{
  "node": {
    "role": "${NODE_ROLE}",
    "site_name": "${NODE_SITE_NAME}",
    "secret_key": "${NODE_SECRET_KEY}",
    "hub_url": "${NODE_HUB_URL}"
  },
  "chrony": {
    "gps_refclock": ${GPS_REFCLOCK},
    "pps_refclock": ${PPS_REFCLOCK},
    "gps_server_ip": "${GPS_SOURCE_IP}",
    "makestep": true
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
    echo -e "    1. ${BOLD}Reboot${NC} if prompted above (UART/PPS changes need a reboot)"
    echo -e "    2. On the PTP Master, install PTPScope with role 'PTP Master'"
    echo -e "    3. Use the same secret key on both machines"
    echo -e "    4. Enter this node's IP (${IP_ADDR}) when prompted for GPS Source IP"
    echo ""
fi

if [[ "$NODE_ROLE" == "ptp_master" ]]; then
    echo -e "  ${BOLD}Next steps:${NC}"
    if [[ -n "$GPS_SOURCE_IP" ]]; then
        echo -e "    1. Chrony is already configured to sync from GPS Source at ${GPS_SOURCE_IP}"
        echo -e "    2. In the web UI → Settings → Node, set the GPS Source secret key"
    else
        echo -e "    1. In the web UI → Settings → Chrony, enter the GPS Source IP"
        echo -e "       (this writes the config and restarts chrony automatically)"
        echo -e "    2. In Settings → Node, set the GPS Source secret key"
    fi
    echo ""
    if [[ -n "${TS_MODE:-}" ]]; then
        echo -e "  ${BOLD}Timestamping:${NC}  ${TS_MODE}"
    fi
    echo ""
fi

echo -e "  ${BOLD}Service commands:${NC}"
echo -e "    sudo systemctl status ptpscope"
echo -e "    sudo systemctl restart ptpscope"
echo -e "    sudo journalctl -u ptpscope -f"
echo ""
echo -e "  ${BOLD}Update PTPScope:${NC}"
echo -e "    sudo curl -fsSL -o /opt/ptpscope/ptpscope.py https://raw.githubusercontent.com/itconor/PtPscope/main/ptpscope.py && sudo systemctl restart ptpscope"
echo ""

if $REBOOT_NEEDED; then
    echo -e "  ${YELLOW}${BOLD}⚠  REBOOT REQUIRED${NC}"
    echo -e "  ${YELLOW}Serial UART and/or PPS GPIO changes need a reboot to take effect.${NC}"
    echo -e "  ${YELLOW}Run: sudo reboot${NC}"
    echo ""
fi

echo -e "  ${GREEN}${BOLD}PTPScope is ready.${NC}"
echo ""
