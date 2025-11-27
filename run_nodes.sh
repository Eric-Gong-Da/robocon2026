#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$PROJECT_ROOT/config/nodes.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

NODES=$(python3 -c "
import json
import sys

with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

enabled_nodes = [node for node in config['nodes'] if node.get('enabled', True)]

for node in enabled_nodes:
    print(f\"{node['name']}|{node['path']}|{node.get('description', '')}\")
")

if [ -z "$NODES" ]; then
    echo "No enabled nodes found in configuration"
    exit 0
fi

PIDS=()

cleanup() {
    echo ""
    echo "Shutting down nodes..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
        fi
    done
    wait
    echo "All nodes stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting nodes from $CONFIG_FILE"
echo "=================================="

while IFS='|' read -r name path desc; do
    node_path="$PROJECT_ROOT/$path"
    
    if [ ! -f "$node_path" ]; then
        echo "Warning: Node file not found: $node_path"
        continue
    fi
    
    echo "Starting $name: $desc"
    echo "  Path: $node_path"
    
    python3 "$node_path" &
    pid=$!
    PIDS+=($pid)
    
    echo "  PID: $pid"
    echo ""
done <<< "$NODES"

if [ ${#PIDS[@]} -eq 0 ]; then
    echo "No nodes were started"
    exit 1
fi

echo "All nodes started. Press Ctrl+C to stop all."
echo "=================================="
echo ""

wait
