from pathlib import Path
from catalyst.core.inventory import Inventory
from catalyst.core.executor import Executor
from catalyst.core.logger import get_logger

# Set up logging
logger = get_logger("catalyst.example", level="DEBUG")

def main():
    # Load inventory
    inventory_path = Path("examples/inventory.yaml")
    
    # Save example inventory if it doesn't exist
    if not inventory_path.exists():
        with open(inventory_path, "w") as f:
            f.write(example_inventory)
        logger.info(f"Created example inventory at {inventory_path}")

    # Load inventory
    inventory = Inventory.from_yaml(inventory_path)
    logger.info(f"Loaded {len(inventory.hosts)} hosts from inventory")

    # Execute commands on hosts
    for host_name, host in inventory.hosts.items():
        logger.info(f"Connecting to {host_name}")
        
        try:
            executor = Executor(
                hostname=host.hostname,
                username=host.username,
                password=host.password,
                key_filename=host.key_file
            )

            # Execute a simple command
            result = executor.execute("uname -a")
            
            if result["status"] == 0:
                logger.info(f"Success on {host_name}: {result['stdout']}")
            else:
                logger.error(f"Error on {host_name}: {result['stderr']}")

        except Exception as e:
            logger.error(f"Failed to execute on {host_name}: {str(e)}")
        
        finally:
            executor.close()

if __name__ == "__main__":
    main()

