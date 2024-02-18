import os

import paramiko
from dotenv import load_dotenv
from scp import SCPClient

# Read a .env file to get the SSH credentials
load_dotenv()


def get_raspberry_json():
    # Raspberry Pi's SSH credentials
    hostname = os.getenv("HOSTNAME")
    port = os.getenv("PORT")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    # Path to the JSON file on the Raspberry Pi
    remote_json_path = "/home/igomisp/token.json"

    # Local path to save the downloaded JSON file
    local_json_path = "current_tokens.json"

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    # Use SCP to retrieve the JSON file
    with SCPClient(ssh.get_transport()) as scp:
        scp.get(remote_json_path, local_json_path)

    # Close the SSH connection
    ssh.close()

    print(f"JSON file downloaded to {local_json_path}")
