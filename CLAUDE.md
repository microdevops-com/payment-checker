# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Checks payment/billing status for multiple hosting provider accounts (Hetzner, RedSwitches, VSys, Scaleway, KnownSRV, PraHost) using headless Playwright browser automation, then writes results to Google Sheets and sends Telegram alerts. Designed to run as a daily cron job via Docker.

## Running

This project is **Dockerized** — the normal way to run it is via Docker:

```bash
# Build
docker build -t payment-checker .

# Run (mount config and secrets from host)
docker run --rm \
    -v /path/to/secret.json:/app/secret.json \
    -v /path/to/config.yaml:/app/config.yaml \
    -v /path/to/screenshots:/app/screenshots \
    payment-checker
```

The entrypoint inside the container is `python /app/payment-checker.py --config /app/config.yaml`.

## Configuration

- `config.yaml` — main config (see `config.yaml.example`). Mounts into `/app/config.yaml`.
- `secret.json` — Google Service Account JSON key. Mounts into `/app/secret.json`.
- Screenshots are written to the `cd:` working directory defined in `config.yaml` (`/app` inside Docker, mapped to a host path).

## Known dependency constraint

`setuptools` must be pinned to `<80` in `requirements.txt`. `playwright-stealth==1.0.6` uses `pkg_resources` which breaks with `setuptools>=80` (restructured in that release). Do not remove this pin until `playwright-stealth` is upgraded to a version that uses `importlib.metadata`.

## Code Style Guidelines

- **Imports**: Group standard library imports first, then third-party packages, then local modules
- **Formatting**: Use 4 spaces for indentation
- **Error Handling**: Use try/except blocks with specific exception handling
- **Naming**: Use snake_case for functions and variables, CamelCase for classes
- **Browser Automation**: Take screenshots at key steps for debugging
- **Config**: Use YAML for configuration, never hardcode credentials

## Adding a new provider

Each provider is a separate module (e.g. `hetzner.py`, `scaleway.py`). Follow the same pattern: implement a function that accepts account config, uses Playwright to log in and scrape the balance/invoice status, and returns a result compatible with the common reporting layer in `common.py`. Register the new type in `payment-checker.py`.
