import logging
from typing import Dict, Optional, Tuple, Union
import paramiko
from catalyst.utils.logger import get_logger

class ExecutionError(Exception):
    """Custom exception for execution errors"""
    pass

class Executor:
    """
    Core execution engine for Catalyst that handles remote operations via SSH.
    """
    
    def __init__(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        timeout: int = 30
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None
        self.logger = get_logger(__name__)

    def connect(self) -> None:
        """Establish SSH connection to the target host"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.logger.info(f"Connecting to {self.hostname} as {self.username}")
            
            connect_kwargs = {
                "hostname": self.hostname,
                "username": self.username,
                "port": self.port,
                "timeout": self.timeout,
            }

            if self.password:
                connect_kwargs["password"] = self.password
            if self.key_filename:
                connect_kwargs["key_filename"] = self.key_filename

            self.client.connect(**connect_kwargs)
            self.logger.info(f"Successfully connected to {self.hostname}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.hostname}: {str(e)}")
            raise ExecutionError(f"Connection failed: {str(e)}")

    def execute(
        self,
        command: str,
        sudo: bool = False,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Union[str, int]]:
        """
        Execute a command on the remote host
        
        Args:
            command: The command to execute
            sudo: Whether to execute with sudo
            env: Environment variables to set
            
        Returns:
            Dict containing stdout, stderr, and exit status
        """
        if not self.client:
            self.connect()

        if sudo:
            command = f"sudo {command}"

        try:
            self.logger.debug(f"Executing command: {command}")
            
            # Prepare environment
            env_str = " ".join(f"{k}={v}" for k, v in (env or {}).items())
            if env_str:
                command = f"{env_str} {command}"

            # Execute command
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # Get results
            exit_status = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode().strip()
            stderr_str = stderr.read().decode().strip()

            # Log results
            if exit_status != 0:
                self.logger.warning(
                    f"Command exited with status {exit_status}: {stderr_str}"
                )
            else:
                self.logger.debug("Command executed successfully")

            return {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "status": exit_status
            }

        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            raise ExecutionError(f"Execution failed: {str(e)}")

    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        mode: Optional[int] = None
    ) -> None:
        """
        Upload a file to the remote host
        
        Args:
            local_path: Path to local file
            remote_path: Destination path on remote host
            mode: Optional file mode (e.g., 0o644)
        """
        if not self.client:
            self.connect()

        try:
            sftp = self.client.open_sftp()
            self.logger.info(f"Uploading {local_path} to {remote_path}")
            
            sftp.put(local_path, remote_path)
            
            if mode is not None:
                sftp.chmod(remote_path, mode)
                
            sftp.close()
            self.logger.info("File uploaded successfully")
            
        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise ExecutionError(f"Upload failed: {str(e)}")

    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> None:
        """
        Download a file from the remote host
        
        Args:
            remote_path: Path to file on remote host
            local_path: Destination path on local machine
        """
        if not self.client:
            self.connect()

        try:
            sftp = self.client.open_sftp()
            self.logger.info(f"Downloading {remote_path} to {local_path}")
            
            sftp.get(remote_path, local_path)
            sftp.close()
            
            self.logger.info("File downloaded successfully")
            
        except Exception as e:
            self.logger.error(f"File download failed: {str(e)}")
            raise ExecutionError(f"Download failed: {str(e)}")

    def close(self) -> None:
        """Close the SSH connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info(f"Closed connection to {self.hostname}")

