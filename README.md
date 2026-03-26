# PTPScope

GPS-disciplined PTP Grandmaster with hub/spoke architecture and web UI.

PTPScope supports two deployment modes:

1. **Standalone** — Single Raspberry Pi with GPS HAT acts as both GPS receiver and PTP grandmaster (original behaviour).
2. **Hub/Spoke** — A Raspberry Pi with GPS HAT (**GPS Source**) sends heartbeats to a separate machine with a hardware PTP NIC (**PTP Master**). Each node has its own web UI; the PTP Master dashboard shows live data from both machines.

## Hub/Spoke Architecture

```
  GPS Satellites
       |
  [Raspberry Pi — GPS Source]   ← GPS HAT (NMEA + PPS)
       |  Chrony stratum-1 NTP
       |  HMAC-signed heartbeats (every 10 s)
       ↓
  [PTP Master — hardware NIC]   ← ptp4l + phc2sys grandmaster
       |  PTP IEEE 1588
  [Network Switch]
     / | \
  PTP Slaves (AoIP, broadcast gear, cameras, etc.)
```

The GPS Source runs Chrony as a stratum-1 NTP server (GPS+PPS disciplined). The PTP Master syncs its system clock from the GPS Source via NTP, then disciplines the hardware PHC from the system clock via `phc2sys`, then distributes PTP to the network via `ptp4l`.

## Features

- **Hub/spoke split** — GPS Source and PTP Master are separate machines; both have web dashboards
- **Signed heartbeats** — GPS Source → PTP Master every 10 s, HMAC-SHA256 authenticated
- **GPS time source** — Reads NMEA from the Adafruit Ultimate GPS HAT via serial, PPS on GPIO 4
- **PTP grandmaster** — Manages `ptp4l` and `phc2sys` with automatic restart
- **PHC offset tracking** — Displays hardware clock offset (phc2sys) separately from PTP port offset
- **Chrony / NTP monitoring** — Stratum, offset, frequency drift, NTP sources
- **Hardware timestamping** — Auto-detects hardware vs software timestamping
- **Role-aware dashboard** — GPS Source shows GPS + Chrony + Hub Connection cards; PTP Master shows GPS Source card (remote data) + PTP/PHC + Chrony + System cards
- **Configuration UI** — Full settings including Node role selector with key generation
- **Metric history** — SQLite time-series, canvas charts (offset, delay, HDOP, temp) over 1h/6h/24h
- **Live logs** — `ptp4l` output and application log in the browser
- **Security** — CSRF protection, CSP nonces, PBKDF2 password hashing, session timeouts

## Requirements

### GPS Source node
- Raspberry Pi 3, 4, or 5
- [Adafruit Ultimate GPS HAT](https://www.adafruit.com/product/2324) (or any NMEA GPS with PPS on GPIO 4)
- Raspberry Pi OS (Bookworm recommended)
- Ethernet connection

### PTP Master node
- Any Linux machine
- Network interface with hardware timestamping (e.g. Intel I210, I350) for best accuracy
- `linuxptp` (`ptp4l` / `phc2sys`)
- Ethernet connection

## Quick Start — Hub/Spoke

### 1. Install on GPS Source Pi

```bash
cd ptpscope
sudo bash install_ptpscope.sh
# Select: 1) GPS Source
# Enter a site name, e.g. "gps-pi"
# Enter or generate a shared secret key — COPY IT
# Enter PTP Master URL, e.g. http://192.168.1.100:5001
sudo reboot   # required for UART/PPS changes
```

### 2. Install on PTP Master

```bash
cd ptpscope
sudo bash install_ptpscope.sh
# Select: 2) PTP Master
# Enter a site name, e.g. "ptp-master"
# Paste the same shared secret key from step 1
```

### 3. Point Chrony on PTP Master at GPS Source

```bash
sudo nano /etc/chrony/chrony.conf
# Add: server <gps-pi-ip> iburst prefer
# Add: makestep 1 3
sudo systemctl restart chrony
```

### 4. Open the dashboards

- GPS Source: `http://<gps-pi-ip>:5001`
- PTP Master: `http://<ptp-master-ip>:5001`

The PTP Master dashboard shows a **GPS Source** card with live data from the Pi, plus its own PTP, Chrony, and System cards.

## Quick Start — Standalone

```bash
cd ptpscope
sudo bash install_ptpscope.sh
# Select: 3) Standalone
sudo reboot
```

Open `http://<your-pi-ip>:5001`.

## Dashboard Cards by Role

| Card | Standalone | GPS Source | PTP Master |
|------|-----------|------------|------------|
| GPS Receiver (local) | ✓ | ✓ | — |
| GPS Source (remote heartbeat) | — | — | ✓ |
| PTP Grandmaster + PHC Offset | ✓ | — | ✓ |
| System Clock (Chrony) | ✓ | ✓ | ✓ |
| System Stats | ✓ | ✓ | ✓ |
| Hub Connection | — | ✓ | — |

## Configuration

All settings are configurable via the web UI → **Configuration**:

- **PTP** — Domain, interface, transport, priority, clock class/accuracy, auto-start
- **GPS** — Serial port, baud rate, PPS GPIO pin
- **Chrony** — Refclocks, NTP servers, client access
- **Network** — Web UI port, bind address
- **Security** — Login, username/password, session timeout
- **Node** — Role selector, site name, shared secret key, PTP Master URL

## Service Management

```bash
sudo systemctl status ptpscope
sudo systemctl restart ptpscope
sudo systemctl stop ptpscope
sudo journalctl -u ptpscope -f
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | Role-aware JSON status |
| `POST` | `/api/gps_heartbeat` | Receive GPS node heartbeat (ptp_master only, HMAC secured) |
| `POST` | `/api/ptp/start` | Start ptp4l + phc2sys |
| `POST` | `/api/ptp/stop` | Stop ptp4l + phc2sys |
| `POST` | `/api/ptp/restart` | Restart ptp4l |
| `GET` | `/api/logs` | PTP4L and application log lines |
| `POST` | `/api/logs/clear` | Clear log buffers |
| `GET` | `/api/metrics?metric=X&hours=Y` | Time-series data for charts |

## File Structure

```
ptpscope/
  ptpscope.py              # Single-file Flask app
  install_ptpscope.sh       # Installer (supports all three roles)
  static/                   # Static assets (icons)
  README.md                 # This file
```

Runtime files (created automatically at `/opt/ptpscope/`):

```
  ptpscope_config.json      # Configuration (role, secrets, etc.)
  ptpscope_metrics.db       # SQLite time-series database
  .flask_secret             # Session secret key
  venv/                     # Python virtual environment
```

## Hardware Timestamping Notes

- **Raspberry Pi 4/5** — BCM2711/2712 Ethernet supports hardware timestamping (~100 ns accuracy)
- **Raspberry Pi 3** — Software timestamping only (~10–100 µs)
- **Intel I210/I350 NICs** — Excellent hardware timestamping for the PTP Master role

The installer auto-detects and configures accordingly.

## License

Same license as SignalScope.
