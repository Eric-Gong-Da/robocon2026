# ZMQ Monitor Tool Guide

Complete guide for using the ZMQ monitor tool to debug and inspect robot communication.

## Overview

The ZMQ monitor tool helps you:
- 🔍 **Discover** active publishers across ports
- 📊 **View** real-time data streams
- 🏷️ **Organize** publishers with friendly names
- 🐛 **Debug** communication issues

## Installation

```bash
pip install pyzmq
```

## Quick Start

```bash
cd tools/zmq_monitor

# Discover all active publishers
python monitor.py list

# Monitor sensor data
python monitor.py monitor 5555
```

## Commands

### 1. List Active Publishers

Scans ports to find all active ZMQ publishers and shows their data types.

```bash
python monitor.py list
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

- **Name**: Registered name (or `-` if not registered)
- **Port**: ZMQ port number
- **Host**: Publisher hostname/IP
- **Data Types**: JSON field names and Python types

**Options:**

```bash
# Custom port range
python monitor.py list --start-port 5000 --end-port 6000

# Scan remote host
python monitor.py list --host 192.168.1.10

# Combine
python monitor.py list --start-port 5555 --end-port 5560 --host 192.168.1.10
```

### 2. Monitor a Publisher

Subscribe to a publisher and view live messages in real-time.

**Monitor by port (direct):**

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
  timestamp: 1732745565.1230

[14:32:45.133]
  e1: 45.2800
  e2: -12.4100
  imu: 180.3500
  timestamp: 1732745565.1330
```

- **Timestamp**: Local time when message received (HH:MM:SS.mmm)
- **Float formatting**: 4 decimal places
- **Other types**: Displayed as-is

**Options:**

```bash
# Monitor remote port
python monitor.py monitor 5555 --host 192.168.1.10

# Stop monitoring
Press Ctrl+C
```

### 3. Register a Publisher (Optional)

Store a publisher with a friendly name for easier monitoring.

```bash
python monitor.py add sensor_data 5555
```

**With description:**

```bash
python monitor.py add sensor_data 5555 --desc "Arduino encoder and IMU data"
```

**Remote host:**

```bash
python monitor.py add robot_sensors 5555 --host 192.168.1.10 --desc "Robot sensors"
```

**Benefits:**
- Monitor by name instead of port: `monitor sensor_data`
- Self-documenting with descriptions
- Names shown in `list` output

### 4. View Registry

Show all registered publishers.

```bash
python monitor.py registry
```

**Example output:**

```
Name                 Port     Host            Description
--------------------------------------------------------------------------------
sensor_data          5555     localhost       Arduino encoder and IMU data
robot_odom           5556     192.168.1.10    Robot odometry
navigation           5557     localhost       Navigation commands
```

### 5. Remove from Registry

```bash
python monitor.py remove sensor_data
```

## Usage Patterns

### Quick Debugging (No Registration)

Use when you just need to check data quickly:

```bash
# Find what's publishing
python monitor.py list

# Monitor the port you need
python monitor.py monitor 5555
```

**Pros:** Fast, no setup  
**Cons:** Must remember port numbers

### With Registration (Frequent Use)

Use when you work with the same publishers regularly:

```bash
# One-time setup
python monitor.py add sensors 5555 --desc "Chassis sensors"
python monitor.py add motors 5556 --desc "Motor commands"
python monitor.py add vision 5557 --desc "Camera data"

# Daily use
python monitor.py monitor sensors
python monitor.py monitor motors
python monitor.py monitor vision

# Check what you have registered
python monitor.py registry
```

**Pros:** Easy to remember, self-documenting  
**Cons:** Initial setup required

### Multi-Machine Setup

When your robot runs on a different machine:

```bash
# On your laptop (192.168.1.100)

# Discover publishers on robot (192.168.1.10)
python monitor.py list --host 192.168.1.10

# Register for easy access
python monitor.py add robot_sensors 5555 --host 192.168.1.10

# Monitor from laptop
python monitor.py monitor robot_sensors
```

**Network requirements:**
- Both machines on same network
- No firewall blocking ZMQ ports
- Robot IP address known

## Examples

### Example 1: Debug Sensor Data

```bash
# Terminal 1: Start sensor node
cd ../..
./run_nodes.sh

# Terminal 2: Check it's publishing
cd tools/zmq_monitor
python monitor.py list

# Output:
# Name                 Port     Host            Data Types
# sensor_data          5555     localhost       e1:float, e2:float, imu:float, timestamp:float

# Monitor live data
python monitor.py monitor 5555

# Output:
# [14:32:45.123]
#   e1: 45.2300
#   e2: -12.4500
#   imu: 180.3400
#   timestamp: 1732745565.1230
```

### Example 2: Setup Development Environment

```bash
# Register all your publishers once
python monitor.py add sensors 5555 --desc "Arduino sensors (E1, E2, IMU)"
python monitor.py add motors 5556 --desc "Motor control commands"
python monitor.py add odom 5557 --desc "Calculated odometry"

# View registry
python monitor.py registry

# Now you can monitor by name anytime
python monitor.py monitor sensors
python monitor.py monitor motors
python monitor.py monitor odom
```

### Example 3: Remote Robot Debugging

```bash
# Your robot is at 192.168.1.10
# Your laptop is at 192.168.1.100

# Scan robot for publishers
python monitor.py list --host 192.168.1.10 --start-port 5555 --end-port 5565

# Register the interesting ones
python monitor.py add robot_sensors 5555 --host 192.168.1.10
python monitor.py add robot_motors 5556 --host 192.168.1.10

# Monitor from your laptop
python monitor.py monitor robot_sensors
python monitor.py monitor robot_motors
```

### Example 4: Check Message Rate

```bash
# Monitor and watch timestamps
python monitor.py monitor 5555

# Look at timestamp differences:
# [14:32:45.123] timestamp: 1732745565.1230
# [14:32:45.133] timestamp: 1732745565.1330  <- 10ms difference = 100 Hz
# [14:32:45.143] timestamp: 1732745565.1430  <- 10ms difference = 100 Hz
```

## Database

### Location

Publisher registry is stored in:
```
tools/zmq_monitor/publishers.json
```

### Format

```json
{
  "sensor_data": {
    "port": 5555,
    "host": "localhost",
    "description": "Arduino encoder and IMU data"
  },
  "robot_odom": {
    "port": 5556,
    "host": "192.168.1.10",
    "description": "Robot odometry"
  }
}
```

### Manual Editing

You can edit this file directly if needed:

```bash
# Open in editor
nano tools/zmq_monitor/publishers.json

# Or use sed/jq for scripting
```

**Note:** The tool auto-creates this file on first `add` command.

## Troubleshooting

### "No active publishers found"

**Possible causes:**
1. No nodes are running
2. Wrong port range
3. Wrong host
4. Firewall blocking

**Solutions:**
```bash
# Check if nodes are running
ps aux | grep sensor_node

# Try wider port range
python monitor.py list --start-port 5000 --end-port 6000

# Check localhost explicitly
python monitor.py list --host localhost

# Test direct connection
python monitor.py monitor 5555
```

### "Publisher 'name' not found in database"

The name is not registered. Either:

```bash
# Register it first
python monitor.py add name 5555

# Or monitor by port directly
python monitor.py monitor 5555
```

### Remote host not working

**Check network connectivity:**
```bash
# Ping the host
ping 192.168.1.10

# Check port is accessible (if netcat installed)
nc -zv 192.168.1.10 5555
```

**Firewall settings:**
- Allow incoming/outgoing on ZMQ ports (5555-5565)
- Disable firewall temporarily to test

### Only seeing old/stale data

The discovery scan captures one message per port. This is expected. Use `monitor` for live data:

```bash
# List shows a snapshot
python monitor.py list

# Monitor shows live stream
python monitor.py monitor 5555
```

### Data not updating

**Check publisher is sending:**
```bash
# If publisher logs to console, check for output
# E.g., sensor_node prints each message

# Check CPU usage - should be >0% if running
top -p $(pgrep -f sensor_node)
```

**Check subscriber connection:**
- Tool connects correctly if you see ANY messages
- If you see zero messages, publisher might be down
- Try monitoring by port directly: `monitor 5555`

## Advanced Usage

### Scripting

**Automate publisher discovery:**

```bash
# Get all active ports as JSON
python monitor.py list --start-port 5555 --end-port 5565 > active_pubs.txt

# Parse and register
# (Custom script needed)
```

### Integration

**Use in Python scripts:**

```python
import zmq
import sys

# Subscribe to publisher
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'')

# Read messages
while True:
    try:
        data = socket.recv_json(flags=zmq.NOBLOCK)
        # Process data
        print(data)
    except zmq.Again:
        pass
```

### Multiple Monitors

You can run multiple monitor instances simultaneously:

```bash
# Terminal 1
python monitor.py monitor 5555

# Terminal 2
python monitor.py monitor 5556

# Terminal 3
python monitor.py list  # Works in parallel
```

## Command Reference

```bash
# List active publishers
python monitor.py list [--host HOST] [--start-port PORT] [--end-port PORT]

# Monitor by port or name
python monitor.py monitor <name_or_port> [--host HOST]

# Register publisher
python monitor.py add <name> <port> [--host HOST] [--desc DESCRIPTION]

# Show registry
python monitor.py registry

# Remove from registry
python monitor.py remove <name>

# Help
python monitor.py --help
python monitor.py <command> --help
```

## Tips

1. **Register publishers you use often** - saves typing
2. **Use descriptions** - helps remember what each publisher does
3. **Check `list` first** - before monitoring, verify publisher exists
4. **Monitor during development** - leave it running in a terminal
5. **Use port ranges** - scan narrow ranges for faster discovery

---

**Built with [Qoder](https://qoder.com)**
