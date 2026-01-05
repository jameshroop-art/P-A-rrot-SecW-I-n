# PnP Device Monitor

## Overview
This monitors USB device plug/unplug events using Linux udev and matches devices to Windows drivers.

## Building

```bash
# Install libudev development files first
sudo apt-get install libudev-dev

# Build
gcc -o pnp_monitor pnp_monitor.c -ludev
```

## Running

```bash
sudo ./pnp_monitor
```

**Note**: Requires root privileges to monitor udev events.

## What It Does

1. Monitors udev for USB device events
2. Extracts device VID/PID
3. Looks up matching Windows driver in database
4. Simulates loading the appropriate driver

## Example Output

```
╔═══════════════════════════════════════════════╗
║  PnP Device Monitor - Proof of Concept       ║
║  ParrotWinKernel Project                      ║
╚═══════════════════════════════════════════════╝

Monitoring USB device events...
Press Ctrl+C to exit

Waiting for USB device events...

╔═══════════════════════════════════════════════╗
║  USB DEVICE PLUGGED IN                        ║
╚═══════════════════════════════════════════════╝
Device Node: /dev/bus/usb/001/042
Subsystem: usb
VID:PID: 0x1234:0x5678
Manufacturer: Acme Corp
Product: USB Widget
  ✓ Found driver: My USB Device
  → Loading Windows driver: /opt/drivers/mydevice.sys
  → Driver loaded successfully! (simulated)

╔═══════════════════════════════════════════════╗
║  USB DEVICE UNPLUGGED                         ║
╚═══════════════════════════════════════════════╝
Device Node: /dev/bus/usb/001/042
VID:PID: 0x1234:0x5678
  → Driver unloaded (simulated)
```

## Real Implementation

In production, this would:
- Load actual Windows drivers using the driver loader
- Create device bridges between Linux and Windows space
- Handle driver initialization with real device info
- Manage driver lifecycle (load/unload/reload)
