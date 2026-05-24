import datetime
import requests

API_BASE = "https://api.bunny.net"


def _get(api_key, path, proxy=None):
    url = API_BASE + path
    headers = {"AccessKey": api_key}
    proxies = {"http": proxy["server"], "https": proxy["server"]} if proxy else None
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.status_code != 200:
        raise Exception(f"Bunny CDN API error {response.status_code}: {response.text}")
    return response.json()


def bunny(api_key, balance_threshold, days_threshold, item_number, proxy):

    user = _get(api_key, "/user", proxy)
    account_name = user.get("CompanyName") or user.get("Email", "Unknown")

    # Account hard-disabled or suspended
    if user.get("Suspended") or user.get("AccountDisabled"):
        return f"{account_name} | $0.00", "N/A", False

    billing = _get(api_key, "/billing", proxy)
    balance = billing.get("Balance", 0)
    this_month_charges = billing.get("ThisMonthCharges", 0)
    billing_enabled = billing.get("BillingEnabled", True)

    account_details = f"{account_name} | ${balance:.2f}"

    # Projected days the current balance will last at this month's burn rate
    if this_month_charges > 0:
        days_elapsed = datetime.datetime.utcnow().day  # 1–31
        daily_burn_rate = this_month_charges / days_elapsed
        days_remaining = int(balance / daily_burn_rate)
    else:
        days_remaining = "N/A"

    # Alert if balance or projected days fall below configured thresholds,
    # or if billing is disabled on the account
    if not billing_enabled:
        payment_status = False
    elif balance < balance_threshold:
        payment_status = False
    elif days_remaining != "N/A" and days_remaining < days_threshold:
        payment_status = False
    else:
        payment_status = True

    return account_details, days_remaining, payment_status
