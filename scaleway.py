import datetime
import calendar
import requests

def scaleway(access_key, secret_key, item_number, proxy):

    # cURL example
    # curl -X GET -H "X-Auth-Token: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" "https://api.scaleway.com/billing/v2beta1/invoices"
    url = "https://api.scaleway.com/billing/v2beta1/invoices"
    headers = {
        "X-Auth-Token": secret_key,
        "Content-Type": "application/json"
    }
    if proxy is not None:
        proxy = {
            "http": proxy["server"],
            "https": proxy["server"]
        }
    else:
        proxy = None
    print("Using proxy:", proxy)
    response = requests.get(url, headers=headers, proxies=proxy)

    # If response.status_code is not 200, raise an exception
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    invoices = response.json().get("invoices")
    organisation_name = invoices[0]["organization_name"]

    # Get the due date
    due_date = invoices[0]["due_date"]
    # Convert the due date to a datetime object
    due_date = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    # Get the current date
    current_date = datetime.datetime.now()
    # Calculate the difference in days
    days_remaining = (due_date - current_date).days

    if invoices[0]["state"] != "paid":
        payment_status = False
    else:
        payment_status = True
    
    return organisation_name, days_remaining, payment_status
