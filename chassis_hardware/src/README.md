# Chassis Hardware Nodes

## Sensor Node

Reads encoder and IMU data from Arduino and publishes via ZMQ.

### Configuration

Edit `config/sensor_config.json` in project root:

```json
{
  "serial": {
    "port": "/dev/cu.usbmodem11401",
    "baud_rate": 921600,
    "timeout": 1
  },
  "encoders": {
    "e1": {
      "pin_a": 2,
      "pin_b": 3,
      "description": "Left encoder"
    },
    "e2": {
      "pin_a": 4,
      "pin_b": 5,
      "description": "Right encoder"
    }
  },
  "imu": {
    "enabled": true,
    "description": "IMU heading sensor"
  },
  "zmq": {
    "port": 5555,
    "publish_rate_hz": 100
  }
}
```

### Parameters

**Serial:**
- `port`: Serial port path (find with `ls /dev/cu.*` on macOS or `ls /dev/ttyUSB*` on Linux)
- `baud_rate`: Must match Arduino code (default: 921600)
- `timeout`: Read timeout in seconds

**Encoders:**
- `pin_a`: Arduino pin for encoder A channel
- `pin_b`: Arduino pin for encoder B channel
- `description`: Human-readable label

**IMU:**
- `enabled`: Enable/disable IMU readings

**ZMQ:**
- `port`: ZMQ publisher port
- `publish_rate_hz`: Target publish rate (informational, actual rate depends on Arduino)

### Running

**Standalone:**
```bash
python sensor_node.py
```

**Via launcher:**
```bash
cd ../..
./run_nodes.sh
```

### Published Data

```json
{
  "e1": 45.23,
  "e2": -12.45,
  "imu": 180.34,
  "timestamp": 1732745565.123
}
```

### Monitoring

```bash
cd ../../tools/zmq_monitor
python monitor.py list
python monitor.py monitor 5555
```