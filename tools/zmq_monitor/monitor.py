import zmq
import argparse
import json
import time
import os
from collections import defaultdict
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), 'publishers.json')


class PublisherDB:
    def __init__(self):
        self.db_path = DB_PATH
        self.publishers = self._load()
    
    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.publishers, f, indent=2)
    
    def add(self, name, port, host='localhost', description=''):
        self.publishers[name] = {
            'port': port,
            'host': host,
            'description': description
        }
        self._save()
        print(f"Added publisher '{name}' -> {host}:{port}")
    
    def remove(self, name):
        if name in self.publishers:
            del self.publishers[name]
            self._save()
            print(f"Removed publisher '{name}'")
        else:
            print(f"Publisher '{name}' not found")
    
    def get(self, name):
        return self.publishers.get(name)
    
    def list_all(self):
        if not self.publishers:
            print("No registered publishers.")
            return
        
        print(f"{'Name':<20} {'Port':<8} {'Host':<15} {'Description'}")
        print("-" * 80)
        for name, info in self.publishers.items():
            port = info['port']
            host = info['host']
            desc = info.get('description', '')
            print(f"{name:<20} {port:<8} {host:<15} {desc}")


class ZMQMonitor:
    def __init__(self):
        self.context = zmq.Context()
        self.db = PublisherDB()
    
    def discover_and_list(self, ports=range(5555, 5565), host='localhost', timeout=500):
        print("Scanning for active publishers...\n")
        
        active_pubs = []
        registered = self.db.publishers
        
        for port in ports:
            socket = self.context.socket(zmq.SUB)
            socket.setsockopt(zmq.SUBSCRIBE, b'')
            socket.setsockopt(zmq.RCVTIMEO, timeout)
            
            try:
                socket.connect(f"tcp://{host}:{port}")
                data = socket.recv_json()
                
                name = None
                for reg_name, reg_info in registered.items():
                    if reg_info['port'] == port and reg_info['host'] == host:
                        name = reg_name
                        break
                
                if isinstance(data, dict):
                    data_types = {k: type(v).__name__ for k, v in data.items()}
                else:
                    data_types = type(data).__name__
                
                active_pubs.append({
                    'name': name or '-',
                    'port': port,
                    'host': host,
                    'data_types': data_types
                })
                
            except zmq.Again:
                pass
            except Exception:
                pass
            finally:
                socket.close()
        
        if not active_pubs:
            print("No active publishers found.")
            return
        
        print(f"{'Name':<20} {'Port':<8} {'Host':<15} {'Data Types'}")
        print("-" * 90)
        
        for pub in active_pubs:
            name = pub['name']
            port = pub['port']
            host = pub['host']
            
            if isinstance(pub['data_types'], dict):
                types_str = ', '.join([f"{k}:{v}" for k, v in pub['data_types'].items()])
            else:
                types_str = pub['data_types']
            
            print(f"{name:<20} {port:<8} {host:<15} {types_str}")
    
    def monitor_publisher(self, name_or_port, host='localhost'):
        if name_or_port.isdigit():
            port = int(name_or_port)
            addr = f"tcp://{host}:{port}"
        else:
            info = self.db.get(name_or_port)
            if not info:
                print(f"Publisher '{name_or_port}' not found in database")
                print("Use 'list' to see registered publishers or 'add' to register a new one")
                return
            port = info['port']
            host = info['host']
            addr = f"tcp://{host}:{port}"
        
        socket = self.context.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, b'')
        socket.connect(addr)
        
        print(f"Monitoring {addr}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                try:
                    data = socket.recv_json(flags=zmq.NOBLOCK)
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    
                    if isinstance(data, dict):
                        print(f"[{timestamp}]")
                        for key, value in data.items():
                            if isinstance(value, float):
                                print(f"  {key}: {value:.4f}")
                            else:
                                print(f"  {key}: {value}")
                        print()
                    else:
                        print(f"[{timestamp}] {data}\n")
                    
                except zmq.Again:
                    time.sleep(0.01)
                    
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
        finally:
            socket.close()


def main():
    parser = argparse.ArgumentParser(description='ZMQ Publisher Monitor')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    list_parser = subparsers.add_parser('list', help='List active publishers (scan ports)')
    list_parser.add_argument('--host', default='localhost', help='Host to scan (default: localhost)')
    list_parser.add_argument('--start-port', type=int, default=5555, help='Start port (default: 5555)')
    list_parser.add_argument('--end-port', type=int, default=5565, help='End port (default: 5565)')
    
    reg_parser = subparsers.add_parser('registry', help='Show registered publishers')
    
    add_parser = subparsers.add_parser('add', help='Add a publisher to database')
    add_parser.add_argument('name', help='Publisher name')
    add_parser.add_argument('port', type=int, help='Port number')
    add_parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    add_parser.add_argument('--desc', default='', help='Description')
    
    remove_parser = subparsers.add_parser('remove', help='Remove a publisher from database')
    remove_parser.add_argument('name', help='Publisher name to remove')
    
    monitor_parser = subparsers.add_parser('monitor', help='Monitor a publisher by name or port')
    monitor_parser.add_argument('name_or_port', help='Publisher name or port number')
    monitor_parser.add_argument('--host', default='localhost', help='Host (only used if port number given)')
    
    args = parser.parse_args()
    
    monitor = ZMQMonitor()
    
    if args.command == 'list':
        monitor.discover_and_list(
            ports=range(args.start_port, args.end_port),
            host=args.host
        )
    elif args.command == 'registry':
        monitor.db.list_all()
    elif args.command == 'add':
        monitor.db.add(args.name, args.port, args.host, args.desc)
    elif args.command == 'remove':
        monitor.db.remove(args.name)
    elif args.command == 'monitor':
        monitor.monitor_publisher(args.name_or_port, getattr(args, 'host', 'localhost'))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()