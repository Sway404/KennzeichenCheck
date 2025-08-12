import os
import random
import time

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

def check_plates():
    delay = random.randint(1, 3 * 60)
    time.sleep(delay)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    chars = "??"
    nums = "1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.braunschweig.de/digitalisierung-online-services/online-services/wunschkennzeichen.php")

        iframe = page.wait_for_selector("iframe")

        frame = page.frame_locator("iframe")

        frame.locator('input[placeholder="AA"]').fill(chars)
        frame.locator('input[placeholder="12"]').fill(nums)
        page.keyboard.press("Enter")

        page.wait_for_timeout(60000)

        content = frame.locator("body").inner_text()
        if "keine verfügbaren Kennzeichen" in content:
            print(f"No plates available for BS-{chars} {nums}")
        else:
            for frame in page.frames:
                try:
                    frame.evaluate("""
                                const el = document.querySelector('.cdk-overlay-container');
                                if (el) el.remove();
                                const le = document.querySelector('.bs-site-logo--with-breadcrumb');
                                if (le) le.remove();
                            """)
                except Exception as e:
                    print(f"No Access to iFrame: {e}")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            screenshot_path = os.path.join(script_dir, "screenshot.png")
            iframe.screenshot(path=screenshot_path)
            caption = "https://www.braunschweig.de/digitalisierung-online-services/online-services/wunschkennzeichen.php"
            send_telegram_photo_with_caption(bot_token, chat_id, screenshot_path, caption)
        browser.close()

check_plates()
