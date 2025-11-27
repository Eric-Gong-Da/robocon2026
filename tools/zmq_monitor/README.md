# ZMQ Monitor

A lightweight tool to discover and monitor ZMQ publishers with optional name-based registry.

## Features

- **Auto-discovery**: Scan ports to find active publishers with data types
- **Optional registry**: Store publishers with friendly names (optional)
- **Name or port monitoring**: Monitor by name (if registered) or directly by port
- **Live message view**: Subscribe and view real-time messages

## Installation

```bash
pip install pyzmq
```

## Usage

### 1. Discover Active Publishers

Scan ports to find all active publishers and see their data types:

```bash
python monitor.py list
```

**Custom port range:**

```bash
python monitor.py list --start-port 5000 --end-port 6000
```

**Example output:**

```
Scanning for active publishers...

Name                 Port     Host            Data Types
------------------------------------------------------------------------------------------
sensor_data          5555     localhost       e1:float, e2:float, imu:float, timestamp:float
-                    5556     localhost       x:float, y:float, theta:float
robot_odom           5557     localhost       vx:float, vy:float, omega:float
```

*Names are shown if registered, otherwise shows `-`*

### 2. Monitor by Port or Name

**Monitor by port (no registration needed):**

```bash
python monitor.py monitor 5555
```

**Monitor by name (if registered):**

```bash
python monitor.py monitor sensor_data
```

**Example output:**

```
Monitoring tcp://localhost:5555
Press Ctrl+C to stop

[14:32:45.123]
  e1: 45.2300
  e2: -12.4500
  imu: 180.3400
  timestamp: 1732745565.123

[14:32:45.133]
  e1: 45.2800
  e2: -12.4100
  imu: 180.3500
  timestamp: 1732745565.133
```

Press `Ctrl+C` to stop monitoring.

### 3. (Optional) Register Publishers

You can optionally register publishers with friendly names:

```bash
python monitor.py add sensor_data 5555 --desc "Arduino encoder and IMU data"
```

**Show registry:**

```bash
python monitor.py registry
```

**Example output:**

```
Name                 Port     Host            Description
--------------------------------------------------------------------------------
sensor_data          5555     localhost       Arduino encoder and IMU data
robot_odom           5556     192.168.1.10    Robot odometry
```

**Remove from registry:**

```bash
python monitor.py remove sensor_data
```

## Quick Reference

```bash
# Discover active publishers (shows data types)
python monitor.py list

# Monitor by port directly
python monitor.py monitor 5555

# Monitor remote port
python monitor.py monitor 5555 --host 192.168.1.10

# (Optional) Register a name for convenience
python monitor.py add sensors 5555 --desc "Chassis sensors"

# Monitor by registered name
python monitor.py monitor sensors

# Show registry
python monitor.py registry

# Remove from registry
python monitor.py remove sensors

# Help
python monitor.py --help
```

## Common Workflows

**Quick debugging (no registration):**
```bash
# Find active publishers
python monitor.py list

# Monitor the one you need
python monitor.py monitor 5555
```

**With registration (for frequent use):**
```bash
# Register once
python monitor.py add sensors 5555 --desc "Chassis sensors"
python monitor.py add motors 5556 --desc "Motor commands"

# Monitor by name anytime
python monitor.py monitor sensors
python monitor.py monitor motors
```

**Multi-machine:**
```bash
# Discover on remote host
python monitor.py list --host 192.168.1.10

# Monitor remote port
python monitor.py monitor 5555 --host 192.168.1.10

# Or register and use name
python monitor.py add robot_sensors 5555 --host 192.168.1.10
python monitor.py monitor robot_sensors
```

## Database

Publisher registry is stored in `publishers.json` in the same directory as `monitor.py`. You can edit it manually if needed:

```json
{
  "sensor_data": {
    "port": 5555,
    "host": "localhost",
    "description": "Arduino encoder and IMU data"
  }
}
```

## Notes

- Database auto-created on first `add` command
- Supports JSON-serialized messages only
- Press `Ctrl+C` to stop monitoring
- Can monitor by port without registration