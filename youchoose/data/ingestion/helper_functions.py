# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Helper functions used to connect to local and remote data sources.
"""
import os
import urllib.parse

import sshtunnel
from dotenv import find_dotenv, load_dotenv


def get_env_parameters() -> dict:
    """
    Load in environment variables for database and ssh connections.

    Returns:
        dict: A dictionary of the variables needed for ssh and database
            connections.
    """
    _ = load_dotenv(find_dotenv())  # evaluates to True

    env_dict = {
        "HOST_IP": os.getenv("HOST_IP", ""),
        "HOST_USER": os.getenv("HOST_USER", ""),
        "SSH_PORT": int(os.getenv("SSH_PORT", 22)),
        "DB_PORT": int(os.getenv("DB_PORT", 5432)),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER", "postgres"),
        "DB_PASSWORD": urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "")),
        "DB_HOST": os.getenv("DB_HOST"),
    }

    return env_dict


def ssh_tunnel(private_key):
    """
    Connect to a host computer through a ssh tunnel.

    Use to connect to a database that is not accessible through a
    public ip address. To open the connections, the following variables need to either
    be exported as environment variables or located in a .env file in the project's
    root directory.

    HOST_IP (IP address) - IP for the host to tunnel to.
    SSH_PORT (int) - Open port on host to ssh through.
    HOST_USER (str) - Username on host computer.
    DB_HOST - Hostname/endpoint of the postgres database.
    DB_PORT (int) - Open port on database for connection.
    DB_USER - Username for the database.
    DB_PASSWORD - Password for the database user.
    DB_NAME - Name of the database to connect to.

    Args:
        private_key (paramiko.RSAKey): RSA key used to connect with host computer.

    Returns:
        tunnel (sshtunnel.SSHTunnelForwarder): The connected ssh tunnel to a host
        computer.
    """
    sshtunnel.SSH_TIMEOUT = 30.0
    sshtunnel.TUNNEL_TIMEOUT = 30.0

    ssh_db_dict = get_env_parameters()

    tunnel = sshtunnel.SSHTunnelForwarder(
        (ssh_db_dict.get("HOST_IP"), ssh_db_dict.get("SSH_PORT")),
        ssh_username=ssh_db_dict.get("HOST_USER"),
        ssh_pkey=private_key,
        remote_bind_address=(ssh_db_dict.get("DB_HOST"), ssh_db_dict.get("DB_PORT")),
    )
    tunnel.start()

    return tunnel
