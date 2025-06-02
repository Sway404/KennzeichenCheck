import random
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

def send_telegram_image(token, chat_id, image_path):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(image_path, "rb") as image:
        files = {"photo": image}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    return response.ok

def check_license_plate():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    delay = random.randint(1, 5 * 60)
    print(f"We're waiting {delay} seconds")
    time.sleep(delay)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://wkz.landkreis-peine.de/wkz/?renderer=responsive")

        if page.is_visible("button:has-text('Weiter')"):
            page.click("button:has-text('Weiter')")
            page.click("button:has-text('Weiter')")

        page.wait_for_selector('input[name="WKZSEARCH_CHARS"]')
        page.fill('input[name="WKZSEARCH_CHARS"]', "??")
        page.fill('input[name="WKZSEARCH_NUMS"]', "1")

        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        if "keine freien" in page.content():
            print("No plates available.")
        else:
            page.click('select[name="WKZRESULTLIST_WKZ"]')
            desktop = Path.home() / "Desktop"
            image_path = desktop / "screenshot.png"
            page.screenshot(path=str(image_path))

        send_telegram_image(bot_token, chat_id, image_path)
        browser.close()

check_license_plate()
