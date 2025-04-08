import pyotp
import datetime
import calendar
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from common import *

def vsys(username, password, twofa_secret, item_number, proxy):

    with sync_playwright() as p:

        print("Checking VSys with a browser for the username:", username)

        # Launch a browser
        browser = p.chromium.launch(
            headless=True,
            proxy=proxy
        )

        # Create a new context with a custom user agent
        context = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Create a new page within the context
        page = context.new_page()
        stealth_sync(page)

        # Check the IP address
        check_my_ip(page, item_number)

        # Logout, somehow it saves the session
        page.goto("https://vsys.host/logout.php")
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-0.png".format(item_number=item_number))

        # Navigate to a website
        page.goto("https://vsys.host/login")
        page.wait_for_load_state("load")
        # There is a div
        # <div id="fullpage-overlay" class="w-hidden">
        # Which blocks the page until it is hidden, delete it every time
        try:
            page.evaluate("document.getElementById('fullpage-overlay').remove()")
        except:
            print("No overlay")
            pass
        page.screenshot(path="screenshots/{item_number}-1.png".format(item_number=item_number))

        # Fill in the username and password fields (check ids in inputs)
        page.type("input#inputEmail", username) 
        page.type("input#inputPassword", password)
        page.screenshot(path="screenshots/{item_number}-1_1.png".format(item_number=item_number))

        # Click on the login button
        # <button id="login" type="submit"
        page.wait_for_load_state("load")
        # If "Your Info" text is present anywhere on the page, then we are already logged in, don't know how it works
        if page.inner_text("body").find("Your Info") != -1:
            print("Already logged in")
        else:
            page.click("button#login")

        try:
            page.evaluate("document.getElementById('fullpage-overlay').remove()")
        except:
            print("No overlay")
            pass
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-2.png".format(item_number=item_number))

        # Get Account Name, it sits between <strong></strong> tags
        account_name = page.inner_text("strong")
        print("Account name:", account_name)

        # Navigate to the invoices page
        page.goto("https://vsys.host/clientarea.php?action=invoices")
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-3.png".format(item_number=item_number))

        # Save html for debugging
        with open("screenshots/{item_number}-3.html".format(item_number=item_number), "w") as f:
            f.write(page.content())

        # No sense to remove overlay here or make screenshots, it will just show Loading...
        # But the invoices data is already there, it is in that table
        # <table id="tableInvoicesList" class="table table-list w-hidden">
        # In that table, in <tbody>, walk through all <tr>
        # First <td> is the invoice number
        # Third <td> os the due date, needed text is in the <span class="w-hidden"> tag
        # Fifth <td> is the status

        # Collect all invoices into a list
        invoices = []
        for tr in page.query_selector_all("table#tableInvoicesList tbody tr"):
            # Take first, third and fifth <td> elements
            td1 = tr.query_selector("td:nth-child(1)")
            td3 = tr.query_selector("td:nth-child(3) span.w-hidden")
            td5 = tr.query_selector("td:nth-child(5)")
            # Append to the list
            # The due date is in format "YYYY-MM-DD", convert to datetime
            due_date = datetime.datetime.strptime(td3.inner_text(), "%Y-%m-%d")
            invoices.append((td1.inner_text(), due_date, td5.inner_text()))

        # Check if there are any unpaid invoices
        if any("Unpaid" in invoice[2] for invoice in invoices):
            # Put them in a list
            unpaid_invoices = [invoice for invoice in invoices if "Unpaid" in invoice[2]]
            # Find the unpaid invoice with the closest due date
            closest_invoice = min(unpaid_invoices, key=lambda x: x[1])
            # Calculate the days remaining
            days_remaining = (closest_invoice[1] - datetime.datetime.now()).days
            payment_status = False
        else:
            # Just return the account name and successfull payment status
            days_remaining = None
            payment_status = True
            
        # Logout
        page.goto("https://vsys.host/logout.php")
        page.wait_for_load_state("load")

        page.close()
        browser.close()
        print("Browser closed")

        return account_name, days_remaining, payment_status
