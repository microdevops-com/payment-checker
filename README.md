# payment-checker

## Description

As Hetzner and most of other cool providers do not provide an API to check the payments status, this script can help you to check it regularly, if you have a lot of accounts to check.
Both providers and consumers (us) are interesed to pay in time, but for some reason they just don't.
I even created a ticket to Hetzner to ask them to provide an API to check the payments status, they received it, but no updates yet.

So one can set up this script, check alerts in telegram chat, pay in time, and avoid suspensions.

The script uses playwright framework (headless browser).

Providers supported:
- [Hetzner](https://hetzner.com/)
- [RedSwitches](https://redswitches.com/)
- [Virtual Systems](https://vsys.host/)
- [Scaleway](https://www.scaleway.com/) - they do provide API for billing ❤️
- [KnownSRV](https://knownsrv.com/)
- [PraHost](https://www.prahost.com/)

Requirements:
- A working directory to put screenshots to (helps to debug).
- Google Service Account to access Google Sheets API and a Sheet to put checked payments.
- Telegram Bot API token to send messages to Telegram and a chat ID to send messages to.
- Docker.

## Setup

1. Create `secret.json` with Google Service Account to access Google Sheets API to put checked payments in a Google Sheet.
2. Create `config.yaml`, put working directory, google sheets, telegram setings there.
3. Define a list of provider accounts to check in `config.yaml`.
4. Build and run the docker container:
   ```bash
   docker build -t payment-checker .
   docker run -it --rm \
       -v /home/user/payment-checker/secret.json:/app/secret.json \
       -v /home/user/payment-checker/config.yaml:/app/config.yaml \
       -v /home/user/payment-checker/screenshots:/app/screenshots payment-checker
   ```
6. Create a cron job like this to check the payments daily in the morning:
   ```
   15 9 * * * docker run --rm -v /home/user/payment-checker/secret.json:/app/secret.json -v /home/user/payment-checker/config.yaml:/app/config.yaml -v /home/user/payment-checker/screenshots:/app/screenshots payment-checker > /home/user/payment-checker/cron.log 2>&1
   ```
