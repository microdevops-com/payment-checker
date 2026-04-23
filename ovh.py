import datetime
import hashlib
import time
import requests

ENDPOINT = "https://eu.api.ovh.com/v1"

def _signed_get(app_key, app_secret, consumer_key, path, proxy=None):
    url = ENDPOINT + path
    ts = str(int(time.time()))
    sig_input = f"{app_secret}+{consumer_key}+GET+{url}++{ts}"
    signature = "$1$" + hashlib.sha1(sig_input.encode()).hexdigest()

    headers = {
        "X-Ovh-Application": app_key,
        "X-Ovh-Consumer": consumer_key,
        "X-Ovh-Timestamp": ts,
        "X-Ovh-Signature": signature,
    }
    proxies = {"http": proxy["server"], "https": proxy["server"]} if proxy else None
    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise Exception(f"OVH API error {response.status_code}: {response.text}")
    return response.json()


def ovh(app_key, app_secret, consumer_key, item_number, proxy):

    me = _signed_get(app_key, app_secret, consumer_key, "/me", proxy)
    account_name = me.get("organisation") or f"{me.get('firstname', '')} {me.get('name', '')}".strip()

    from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    bill_ids = _signed_get(app_key, app_secret, consumer_key, f"/me/bill?date.from={from_date}", proxy)

    if not bill_ids:
        return account_name, "N/A", True

    unpaid = []
    most_recent_date = None

    for bill_id in bill_ids:
        debt = _signed_get(app_key, app_secret, consumer_key, f"/me/bill/{bill_id}/debt", proxy)
        if debt is None:
            continue

        bill_date_str = debt.get("date")
        if bill_date_str:
            bill_date = datetime.datetime.fromisoformat(bill_date_str).astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if most_recent_date is None or bill_date > most_recent_date:
                most_recent_date = bill_date

        if debt.get("status") != "PAID":
            unpaid.append(debt)

    if unpaid:
        due_dates = [
            datetime.datetime.fromisoformat(d["dueDate"]).astimezone(datetime.timezone.utc).replace(tzinfo=None)
            for d in unpaid if d.get("dueDate")
        ]
        days_remaining = (min(due_dates) - datetime.datetime.utcnow()).days if due_dates else "N/A"
        return account_name, days_remaining, False

    days_since = (datetime.datetime.utcnow() - most_recent_date).days if most_recent_date else "N/A"
    return account_name, -days_since, True
