#!/usr/bin/env python3
"""
Generate docker-compose.yml with N server instances
Usage: python generate_compose.py [num_servers]
"""

import sys
import yaml
from typing import Dict, Any


def generate_server_config(server_num: int, base_port: int = 8000) -> Dict[str, Any]:
    """Generate configuration for a single server instance"""
    return {
        f"server-{server_num}": {
            "build": "./server",
            "container_name": f"server-{server_num}",
            "environment": [
                f"SERVER_ID=server-{server_num}",
                "SERVER_PORT=8000"
            ],
            "ports": [
                f"{base_port + server_num}:8000"
            ],
            "restart": "unless-stopped",
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "0.5",
                        "memory": "256M"
                    },
                    "reservations": {
                        "cpus": "0.1",
                        "memory": "128M"
                    }
                }
            },
            "networks": ["server-network"],
            "healthcheck": {
                "test": ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"],
                "interval": "30s",
                "timeout": "3s",
                "start_period": "5s",
                "retries": 3
            }
        }
    }


def generate_docker_compose(num_servers: int = 50, base_port: int = 8000) -> Dict[str, Any]:
    """Generate complete docker-compose configuration"""
    
    compose_config = {
        "version": "3.8",
        "services": {},
        "networks": {
            "server-network": {
                "driver": "bridge"
            }
        }
    }
    
    # Generate all server instances
    for i in range(1, num_servers + 1):
        server_config = generate_server_config(i, base_port)
        compose_config["services"].update(server_config)
    
    return compose_config


def main():
    num_servers = 50
    base_port = 8000
    
    if len(sys.argv) > 1:
        try:
            num_servers = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            base_port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port: {sys.argv[2]}")
            sys.exit(1)
    
    print(f"Generating docker-compose.yml with {num_servers} servers starting at port {base_port}...")
    
    compose_config = generate_docker_compose(num_servers, base_port)
    
    # Write to file
    with open("docker-compose.yml", "w") as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Generated docker-compose.yml successfully!")
    print(f"   Servers: {num_servers}")
    print(f"   Port range: {base_port + 1} - {base_port + num_servers}")
    print(f"\nTo start all servers:")
    print(f"   docker-compose up -d --build")


if __name__ == "__main__":
    main()
