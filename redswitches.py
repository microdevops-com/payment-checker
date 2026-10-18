import re
import pyotp
import datetime
import calendar
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from common import *

def redswitches(username, password, twofa_secret, item_number, proxy):

    with sync_playwright() as p:

        print("Checking RedSwitches with a browser for the username:", username)

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
        page.goto("https://dedicated.redswitches.com/logout.php")
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-0.png".format(item_number=item_number))

        # Navigate to a website
        page.goto("https://dedicated.redswitches.com/index.php?rp=/login")
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
        # <button id="login" type="submit" class="btn btn-primary rs-auth-submit">Login</button>
        # It used to be an <input>, accept both in case the theme changes back
        page.wait_for_load_state("load")
        # Sometimes typing the credentials already lands us in the client area (e.g. the password
        # ends with a newline and submits the form). Wait for either the login button or a sign
        # that we are logged in: the sidebar user menu <span class="rx-me-n"> in the new theme,
        # or the "Your Info" text in the old theme.
        page.wait_for_selector("button#login, input#login, span.rx-me-n")
        if page.query_selector("span.rx-me-n") is not None or page.inner_text("body").find("Your Info") != -1:
            print("Already logged in")
        else:
            page.click("button#login, input#login")

        try:
            page.evaluate("document.getElementById('fullpage-overlay').remove()")
        except:
            print("No overlay")
            pass
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-2.png".format(item_number=item_number))

        # Get Account Name, the new "RedSwitches Cloud" theme shows the user name
        # in the sidebar: <span class="rx-me-n">Name</span>
        account_name = page.inner_text("span.rx-me-n")
        print("Account name:", account_name)

        # Navigate to the invoices page
        page.goto("https://dedicated.redswitches.com/clientarea.php?action=invoices")
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-3.png".format(item_number=item_number))

        # Save html for debugging
        with open("screenshots/{item_number}-3.html".format(item_number=item_number), "w") as f:
            f.write(page.content())

        # The invoices are in that table (new "RedSwitches Cloud" theme)
        # <table class="rx-table" id="rx-invoices">
        # In that table, in <tbody>, walk through all <tr class="rx-row" data-kind="paid|other|unpaid">
        # <td class="rx-c-inv"> holds the invoice number as "#8031"
        # <td class="rx-c-due"> holds the due date as "24th Oct 2026"
        # <td class="rx-c-st"> holds the status: Paid, Unpaid, Cancelled, ...

        # Collect all invoices into a list
        invoices = []
        for tr in page.query_selector_all("table#rx-invoices tbody tr"):
            td_inv = tr.query_selector("td.rx-c-inv")
            td_due = tr.query_selector("td.rx-c-due")
            td_st = tr.query_selector("td.rx-c-st")
            invoice_number = td_inv.inner_text().strip().lstrip("#")
            # The due date is in format "24th Oct 2026", drop the ordinal suffix and convert to datetime
            due_text = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", td_due.inner_text().strip())
            due_date = datetime.datetime.strptime(due_text, "%d %b %Y")
            invoices.append((invoice_number, due_date, td_st.inner_text().strip()))

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
        page.goto("https://dedicated.redswitches.com/logout.php")
        page.wait_for_load_state("load")

        page.close()
        browser.close()
        print("Browser closed")

        return account_name, days_remaining, payment_status
