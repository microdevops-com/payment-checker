def check_my_ip(page, item_number):

    print("Checking IP address...")

    # Navigate to a website
    try:
        page.goto("https://ip.me/")
    except:
        page.goto("https://ifconfig.me/")

    # Print debug information
    print("Page title:", page.title())

    # Take a screenshot of the IP address
    # Full page load sometimes never happen with slow proxys, so we wait for body selector instead
    #page.wait_for_load_state("load")
    page.wait_for_selector("body", timeout=30000)
    page.screenshot(path="screenshots/{item_number}-_ip.png".format(item_number=item_number))
