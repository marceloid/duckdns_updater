import logging
import os
import re
import subprocess
import time

import requests
from dotenv import load_dotenv

load_dotenv()
# --- Configuration ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

DUCKDNS_TOKEN = os.environ.get("DUCKDNS_TOKEN", "YOUR_DUCKDNS_TOKEN")
DUCKDNS_DOMAIN = os.environ.get("DUCKDNS_DOMAIN", "YOUR_DUCKDNS_DOMAIN")
DATA_DIR = "data"
IP_FILE = os.path.join(DATA_DIR, "last_ip.txt")

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 300))
# --- End Configuration ---


def get_ipv6():
    """Gets the current public IPv6 address using an external service."""
    try:
        result = subprocess.run(
            ["curl", "-6", "ip.sb"], capture_output=True, text=True, check=True
        )
        ip = result.stdout.strip()
        logging.debug(f"'curl -6 ip.sb' output: {ip}")

        # Validate the output is a valid IPv6 address
        ipv6_pattern = re.compile(r"^[0-9a-fA-F:]{2,39}$")
        if ipv6_pattern.match(ip):
            return ip
        else:
            logging.error(f"Output from ip.sb is not a valid IPv6 address: {ip}")
            return None

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"Error getting IPv6 address: {e}")
        return None


def read_last_ip():
    """Reads the last known IP address from the IP file."""
    if not os.path.exists(IP_FILE):
        return None
    with open(IP_FILE, "r") as f:
        return f.read().strip()


def write_last_ip(ip):
    """Writes the current IP address to the IP file."""
    with open(IP_FILE, "w") as f:
        f.write(ip)


def update_duckdns(ip):
    """Updates the DuckDNS record with the new IP address."""
    url = f"https://www.duckdns.org/update?domains={DUCKDNS_DOMAIN}&token={DUCKDNS_TOKEN}&ipv6={ip}&verbose=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.text.startswith("OK"):
            logging.info(f"Successfully updated DuckDNS for {DUCKDNS_DOMAIN} to {ip}")
            return True
        else:
            logging.error(f"Error updating DuckDNS: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error updating DuckDNS: {e}")


def main():
    """Checks the current IPv6 address and updates DuckDNS if it has changed."""
    while True:
        current_ip = get_ipv6()
        if not current_ip:
            time.sleep(CHECK_INTERVAL)
            continue

        last_ip = read_last_ip()

        if current_ip != last_ip:
            logging.info(f"IP address has changed from {last_ip} to {current_ip}")
            if update_duckdns(current_ip):
                write_last_ip(current_ip)
        else:
            logging.info(f"IP address ({current_ip}) has not changed.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
