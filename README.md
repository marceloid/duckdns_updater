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

## Publishing a Multi-Platform Image

To ensure your container image runs on different computer architectures (like Intel/AMD `amd64` and Apple Silicon `arm64`), you need to create a multi-platform image.

**Step 1: Set up Docker Buildx**

`buildx` is a Docker component that enables multi-platform builds. Create and switch to a new builder instance (you only need to do this once):

```bash
docker buildx create --name mybuilder --use
```

**Step 2: Authenticate**

You still need to authenticate with a Personal Access Token (PAT) that has the `write:packages` scope.

```bash
export CR_PAT="YOUR_COPIED_TOKEN"
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
```

**Step 3: Build and Push the Image**

This single command will build the image for both `amd64` and `arm64` platforms and push them to `ghcr.io` under a single tag.

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/YOUR_GITHUB_USER/duckdns-updater:latest --push .
```

After the push is complete, you may need to set the package visibility to Public on the GitHub website.

## Running the Application from the Public Image

With the image published to `ghcr.io`, you can run the container on any machine with Docker without needing to build it from source.

**Prerequisites:**

1.  **Docker is installed.**
2.  **A `.env` file** is present in your working directory with your `DUCKDNS_TOKEN` and `DUCKDNS_DOMAIN`.

**Command to Run:**

Execute the following command. Docker will automatically pull the public image from `ghcr.io` and run it.

```bash
docker run -d \
  --name duckdns-updater \
  --restart=always \
  --network host \
  --env-file .env \
  -v duckdns-data:/app/data \
  ghcr.io/YOUR_GITHUB_USER/duckdns-updater:latest
```

### Data Persistence

The `-v duckdns-data:/app/data` flag creates a Docker named volume called `duckdns-data`. This is **critical** to ensure that the last known IP address is not lost if the container is ever removed or updated.

### A Note on Configuration and Data

*   **Environment Variables (`.env` file):** This command uses `--env-file .env` to load your DuckDNS token and domain. This file is stored in plain text on your host. For better security in a production environment, ensure this file is readable only by the user running the container (`chmod 600 .env`). For more advanced setups, consider using a secrets management tool like HashiCorp Vault.

*   **Data Persistence (`-v` flag):** The `-v duckdns-data:/app/data` flag creates a Docker named volume called `duckdns-data`. This volume is mounted into the container at `/app/data`, where the `last_ip.txt` file is stored. This is **critical** to ensure that the last known IP address is not lost if the container is removed and recreated. Without it, the container would start fresh every time and might send unnecessary updates to DuckDNS.
