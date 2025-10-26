# DuckDNS Updater

This script checks your public IPv6 address and updates your DuckDNS domain if the IP address has changed.

## Setup

1.  **Install dependencies:**

    ```bash
    uv pip install -r requirements.txt
    ```

2.  **Set your DuckDNS credentials:**

    Create a `.env` file in the root of the project and add your DuckDNS token and domain:

    ```
    DUCKDNS_TOKEN=YOUR_DUCKDNS_TOKEN
    DUCKDNS_DOMAIN=YOUR_DUCKDNS_DOMAIN
    ```

## Usage

To run the script, execute the following command:

```bash
source .venv/bin/activate
python main.py
```

## Docker

To build the Docker image, run:

```bash
docker build -t duckdns-updater .
```

To run the Docker container:

```bash
docker run -d \
  --name duckdns-updater \
  --restart=always \
  --network host \
  --env-file .env \
  -v duckdns-data:/app/data \
  duckdns-updater
```

### A Note on Configuration and Data

*   **Environment Variables (`.env` file):** This command uses `--env-file .env` to load your DuckDNS token and domain. This file is stored in plain text on your host. For better security in a production environment, ensure this file is readable only by the user running the container (`chmod 600 .env`). For more advanced setups, consider using a secrets management tool like HashiCorp Vault.

*   **Data Persistence (`-v` flag):** The `-v duckdns-data:/app/data` flag creates a Docker named volume called `duckdns-data`. This volume is mounted into the container at `/app/data`, where the `last_ip.txt` file is stored. This is **critical** to ensure that the last known IP address is not lost if the container is removed and recreated. Without it, the container would start fresh every time and might send unnecessary updates to DuckDNS.