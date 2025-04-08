#!/usr/bin/env python3

import calendar
import datetime
import pyotp
from googleapiclient.discovery import build                                                                                                                                                             
import oauth2client.client                                                                                                                                                                              
from google.oauth2 import service_account
import yaml
import time
from common import *
from hetzner import hetzner
from redswitches import redswitches
from vsys import vsys
import os
import requests
import textwrap
import click

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def clear_google_sheet(sa_secrets_file, spreadsheet_id, sheet_name):

    credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=credentials)

    # Clear the sheet starting from the second row
    request = sheets_service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=sheet_name + "!A2:Z")
    response = request.execute()
    print("Cleared the Google Sheet")

def append_google_sheet(sa_secrets_file, spreadsheet_id, sheet_name, row_list):

    credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=credentials)

    # Append the row to the sheet
    request = sheets_service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=sheet_name + "!A:Z", valueInputOption="USER_ENTERED", body={"values": [row_list]})
    response = request.execute()
    print("Appended the row to the Google Sheet")

def remove_screenshots():

    import os

    # Remove all screenshots from the screenshots directory
    # png or html files
    for file in os.listdir("screenshots"):
        if file.endswith(".png") or file.endswith(".html"):
            os.remove("screenshots/" + file)

def alert_telegram(chat_id, token, date, type, login, details, days, status, header):

    # Markdown alert text template
    text = textwrap.dedent(
        """
        {header}
        Date Checked: {date}
        Account Type: {type}
        Login: {login}
        Account Details: {details}
        Days Remaining: {days}
        Payment Status: {status}
        """
    ).format(
        header=header,
        date=date,
        type=type,
        login=login,
        details=details,
        days=days,
        status=status
    )

    # Telegram API URL
    url = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}".format(token=token, chat_id=chat_id, text=text)
    requests.get(url)

@click.command()
@click.option("--config", required=True, help="Path to the config.yaml file")
def main(config):

    with open(config, "r") as stream:
        config = yaml.safe_load(stream)

    # Change working directory to the cd from config file
    os.chdir(config["cd"])

    # Current date in the format of YYYY-MM-DD
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Clear the Google Sheet
    try:
        clear_google_sheet(config["google_sheets"]["sa_secrets_file"], config["google_sheets"]["spreadsheet_id"], config["google_sheets"]["sheet_name"])
    except Exception as e:
        print("Error:", e)
        alert_telegram(config["telegram"]["chat_id"], config["telegram"]["token"], current_date, "---", "---", "---", "---", "---", "ERROR: Google Sheet Clearing Failed")
        exit(1)

    # Remove all screenshots from the screenshots directory
    remove_screenshots()

    # Set this to False if any account has a payment issue
    no_issues = True

    # Iterate over the list of accounts
    item_number = 0
    for account in config["accounts"]:

        item_number += 1

        print("Checking account type {type} for the login {login}".format(**account))

        # Unset the variables
        account_details = "None"
        days_remaining = "None"
        payment_status = "None"

        # Set the proxy
        if "proxy" in account:
            proxy = account["proxy"]
        else:
            proxy = None

        # If there is no 2FA secret, then set it to None
        if "2fa" not in account:
            account["2fa"] = None

        try:

            if account["type"] == "Hetzner":
                account_details, days_remaining, payment_status = hetzner(account["login"], account["password"], account["2fa"], item_number, proxy)
            elif account["type"] == "RedSwitches":
                account_details, days_remaining, payment_status = redswitches(account["login"], account["password"], account["2fa"], item_number, proxy)
            elif account["type"] == "VSys":
                account_details, days_remaining, payment_status = vsys(account["login"], account["password"], account["2fa"], item_number, proxy)

        except Exception as e:
            print("Error:", e)
            account_details = "Error"
            days_remaining = "Error"
            payment_status = "Error"

        # Prepare the row to be written to the Google Sheet
        row_list = [
            current_date,
            account["type"],
            account["login"],
            account_details,
            days_remaining,
            payment_status
        ]

        # Write the data to the Google Sheet
        append_google_sheet(config["google_sheets"]["sa_secrets_file"], config["google_sheets"]["spreadsheet_id"], config["google_sheets"]["sheet_name"], row_list)

        # Send an alert to the Telegram if status is not True
        if payment_status != True:
            alert_telegram(config["telegram"]["chat_id"], config["telegram"]["token"], current_date, account["type"], account["login"], account_details, days_remaining, payment_status, "WARNING: Payment Issue Detected")
            # Also set the no_issues to False
            no_issues = False

        print("---")

        # Take a pause between the accounts just in case
        time.sleep(5)

    # If there are no issues, then send a message to the Telegram
    if no_issues:
        alert_telegram(config["telegram"]["chat_id"], config["telegram"]["token"], current_date, "---", "---", "---", "---", "All accounts are OK", "INFO: All Accounts OK")

if __name__ == "__main__":
    main()
