# src/catalyst/core/inventory.py
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from catalyst.core.logger import get_logger

class InventoryError(Exception):
    """Custom exception for inventory-related errors"""
    pass

class Host:
    """Represents a single host in the inventory"""
    
    def __init__(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        port: int = 22,
        groups: List[str] = None,
        variables: Dict = None
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
        self.port = port
        self.groups = groups or []
        self.variables = variables or {}

    @classmethod
    def from_dict(cls, data: Dict) -> 'Host':
        """Create a Host instance from a dictionary"""
        return cls(
            hostname=data['hostname'],
            username=data['username'],
            password=data.get('password'),
            key_file=data.get('key_file'),
            port=data.get('port', 22),
            groups=data.get('groups', []),
            variables=data.get('variables', {})
        )

class Inventory:
    """Manages the infrastructure inventory"""
    
    def __init__(self):
        self.hosts: Dict[str, Host] = {}
        self.groups: Dict[str, List[str]] = {}
        self.logger = get_logger(__name__)

    def add_host(self, name: str, host: Host) -> None:
        """Add a host to the inventory"""
        self.hosts[name] = host
        for group in host.groups:
            if group not in self.groups:
                self.groups[group] = []
            if name not in self.groups[group]:
                self.groups[group].append(name)
        self.logger.debug(f"Added host: {name}")

    def get_host(self, name: str) -> Host:
        """Get a host by name"""
        if name not in self.hosts:
            raise InventoryError(f"Host not found: {name}")
        return self.hosts[name]

    def get_group_hosts(self, group: str) -> List[Host]:
        """Get all hosts in a group"""
        if group not in self.groups:
            raise InventoryError(f"Group not found: {group}")
        return [self.hosts[host] for host in self.groups[group]]

    @classmethod
    def from_yaml(cls, path: Path) -> 'Inventory':
        """Create an inventory from a YAML file"""
        inventory = cls()
        logger = get_logger(__name__)
        
        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            # Process hosts
            hosts_data = data.get('hosts', {})
            for name, host_data in hosts_data.items():
                host = Host.from_dict(host_data)
                inventory.add_host(name, host)

            # Process groups
            groups_data = data.get('groups', {})
            for group_name, group_data in groups_data.items():
                for host_name in group_data.get('hosts', []):
                    if host_name in inventory.hosts:
                        if group_name not in inventory.hosts[host_name].groups:
                            inventory.hosts[host_name].groups.append(group_name)
                            if group_name not in inventory.groups:
                                inventory.groups[group_name] = []
                            inventory.groups[group_name].append(host_name)

            logger.info(f"Loaded inventory from {path}")
            logger.debug(f"Loaded {len(inventory.hosts)} hosts in {len(inventory.groups)} groups")
            
            return inventory

        except Exception as e:
            logger.error(f"Failed to load inventory from {path}: {str(e)}")
            raise InventoryError(f"Failed to load inventory: {str(e)}")

# Example inventory.yaml structure
example_inventory = '''
hosts:
  web1:
    hostname: web1.example.com
    username: admin
    key_file: ~/.ssh/id_rsa
    groups:
      - webservers
      - production
    variables:
      http_port: 80
      https_port: 443

  db1:
    hostname: db1.example.com
    username: dbadmin
    password: secure_password
    groups:
      - databases
      - production
    variables:
      db_port: 5432

groups:
  webservers:
    variables:
      nginx_enabled: true
  
  databases:
    variables:
      backup_enabled: true
  
  production:
    variables:
      environment: prod
'''
