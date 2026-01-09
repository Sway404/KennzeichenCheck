import os
import random
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

def send_telegram_photo_with_caption(token, chat_id, image_path, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(image_path, "rb") as image:
        files = {"photo": image}
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, files=files, data=data)
    return response.ok

def check_license_plate():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    chars = "??"
    nums = "1"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://wkz.landkreis-peine.de/wkz/?renderer=responsive")

        if page.is_visible("button:has-text('Weiter')"):
            page.click("button:has-text('Weiter')")
            page.click("button:has-text('Weiter')")

        page.wait_for_selector('input[name="WKZSEARCH_CHARS"]')
        page.fill('input[name="WKZSEARCH_CHARS"]', chars)
        page.fill('input[name="WKZSEARCH_NUMS"]', nums)

        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        if "keine freien" in page.content():
            print("No plates available.")
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            screenshot_path = os.path.join(script_dir, "screenshotPE.png")
            page.click('select[name="WKZRESULTLIST_WKZ"]')
            page.screenshot(path=screenshot_path)
            caption = "https://wkz.landkreis-peine.de/wkz/?renderer=responsive"
            send_telegram_photo_with_caption(bot_token, chat_id, screenshot_path, caption)
        browser.close()

check_license_plate()
