def check_my_ip(page, item_number):

    # Navigate to a website
    page.goto("https://ip.me/")

    # Take a screenshot of the IP address
    page.wait_for_load_state("load")
    page.screenshot(path="screenshots/{item_number}-_ip.png".format(item_number=item_number))
