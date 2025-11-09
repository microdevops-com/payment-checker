import pyotp
import datetime
import calendar
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from common import *

def hetzner(username, password, twofa_secret, item_number, proxy):

    with sync_playwright() as p:

        print("Checking Hetzner with a browser for the username:", username)

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

        # Navigate to a website
        page.goto("https://accounts.hetzner.com/login")
        page.wait_for_load_state("load")

        page.screenshot(path="screenshots/{item_number}-1.png".format(item_number=item_number))

        # Fill in the username and password fields (check ids in inputs)
        page.type("input#_username", username) 
        page.type("input#_password", password)

        # Click on the login button
        page.wait_for_load_state("load")
        page.click("input#submit-login")
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-2.png".format(item_number=item_number))

        # If the 2FA code is None, skip the 2FA step
        if twofa_secret is not None:

            # Get the 2FA code
            totp = pyotp.TOTP(twofa_secret)
            otp = totp.now()

            # Fill in the 2FA code
            page.type("input#input-verify-code", otp)

            # Click on the verify button
            page.click("input#btn-submit")
            page.wait_for_load_state("load")
            page.screenshot(path="screenshots/{item_number}-2_1.png".format(item_number=item_number))

        # Get Client Number from <div class="idp-info">
        client_number_text = page.inner_text("div.idp-info")
        print(client_number_text)
        # Extract the client number from the text by removing "Client number: " and keeping the last part
        client_number = client_number_text.split("Client number: ")[1]

        # Navigate to the invoices page
        page.goto('https://accounts.hetzner.com/invoice')
        page.wait_for_load_state("load")
        page.screenshot(path="screenshots/{item_number}-3.png".format(item_number=item_number))

        # Find the invoice creation date
        # Sample: <li class="list-inline-item"><div class="badge badge-blue">12th of the month</div></li>
        invoice_date_text = page.inner_text("li.list-inline-item > div.badge.badge-blue")
        print("The invoice will be created on the following day:", invoice_date_text)

        # Take a number by removing all non digits from the invoice_date_text
        # Sample: 21st of the month
        invoice_date = int(''.join(filter(str.isdigit, invoice_date_text)))

        # Calculate the difference between in days between the current date and the invoice_date in the next invoice_date
        now = datetime.datetime.now()
        current_date = now.day
        # Get the number of days in the current month
        days_in_current_month = calendar.monthrange(now.year, now.month)[1]
        if current_date > invoice_date:
            # In this case, the next invoice date is in the next month
            # Calculate the number of days remaining until the next invoice date
            days_remaining = days_in_current_month - current_date + invoice_date
        elif current_date == invoice_date:
            # In this case, the next invoice date is in one month
            days_remaining = days_in_current_month
        else:
            # In this case, the next invoice date is in the current month
            days_remaining = invoice_date - current_date
        print("Days remaining until the next invoice date:", days_remaining)

        # If <span class="invoice-status status-pending">pending</span> exists, then the invoice is pending
        invoice_status = page.query_selector("span.invoice-status.status-pending")
        if invoice_status:
            print("Found a pending status for the invoice")
            payment_status = False
        else:
            print("No pending status for the invoice found")
            payment_status = True

        browser.close()
        print("Browser closed")

        return client_number, days_remaining, payment_status
