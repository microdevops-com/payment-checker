import requests

API_URL = "https://www.customerpanel.nl/api.php"

def _post(api_key, method, proxy=None):
    proxies = {"http": proxy["server"], "https": proxy["server"]} if proxy else None
    response = requests.post(API_URL, data={"method": method, "api_id": api_key}, proxies=proxies)
    if response.status_code != 200:
        raise Exception(f"Worldstream API error {response.status_code}: {response.text}")
    return response.json()


def worldstream(api_key, item_number, proxy):

    servers = _post(api_key, "get_dedicated_list", proxy)
    names = [
        v["Alias"] or v["Name"]
        for k, v in servers.items()
        if k.isdigit()
    ]
    account_name = ", ".join(names) if names else "Unknown"

    invoices = _post(api_key, "get_open_invoices", proxy)

    if invoices.get("StatusCode") == "1":
        amounts = [
            v["Amount"]
            for k, v in invoices.items()
            if k.isdigit()
        ]
        total = sum(float(a) for a in amounts)
        return account_name, "N/A", False

    return account_name, "N/A", True
