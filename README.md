# payment-checker

## Description

As Hetzner and most of other cool providers do not provide an API to check the payments status, this script can help you to check it regularly, if you have a lot of accounts to check.
Both providers and consumers (us) are interesed to pay in time, but for some reason they just don't.
I even created a ticket to Hetzner to ask them to provide an API to check the payments status, they received it, but no updates yet.

So one can set up this script, check alerts in telegram chat, pay in time, and avoid suspensions.

The script uses playwright framework (headless browser).

Providers supported:
- Hetzner
- RedSwitches

Requirements:
- A working directory to put screenshots to (helps to debug).
- Google Service Account to access Google Sheets API and a Sheet to put checked payments.
- Telegram Bot API token to send messages to Telegram and a chat ID to send messages to.

## Setup

1. Create `secret.json` with Google Service Account to access Google Sheets API to put checked payments in a Google Sheet.
2. Create `config.yaml`, put working directory, google sheets, telegram setings there.
3. Define a list of provider accounts to check in `config.yaml`.
4. Install needed python requirements, setup playwright:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```
5. Check if it works with `payment-checker.py --config /home/user/payment-checker/config.yaml`.
6. Create a cron job like this to check the payments daily in the morning:
   ```
   15 9 * * * /home/user/payment-checker/payment-checker.py --config /home/user/payment-checker/config.yaml > /home/user/payment-checker/cron.log 2>&1
   ```
