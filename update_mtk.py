import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.eredmenyek.com/csapat/mtk-budapest/ppX6bEHk/eredmenyek/"

matches = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        locale="hu-HU",
        timezone_id="Europe/Budapest"
    )

    page = context.new_page()

    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # Megvárjuk az oldal betöltését
    page.wait_for_timeout(5000)

    # A "További meccsek" gombokat többször megpróbáljuk megnyomni
    for _ in range(10):
        try:
            buttons = page.get_by_text("További meccsek", exact=True)
            count = buttons.count()

            if count == 0:
                break

            for i in range(count):
                try:
                    button = buttons.nth(i)

                    if button.is_visible():
                        button.click()
                        page.wait_for_timeout(1500)

                except Exception:
                    continue

        except Exception:
            break

    # Az összes mérkőzéslinket megkeressük
    links = page.locator('a[href*="/merkozes/"]')
    count = links.count()

    for i in range(count):
        try:
            link = links.nth(i)

            text = " ".join(link.inner_text().split())
            href = link.get_attribute("href")

            if not href:
                continue

            if not text:
                continue

            if href.startswith("/"):
                href = "https://www.eredmenyek.com" + href

            stats_url = (
                href.rstrip("/")
                + "/osszefoglalas/statisztika/"
            )

            matches.append({
                "text": text,
                "url": href,
                "stats_url": stats_url
            })

        except Exception:
            continue

    browser.close()

# Duplikációk eltávolítása
unique = {}

for match in matches:
    unique[match["url"]] = match

matches = list(unique.values())

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "source": URL,
    "matches": matches
}

with open("data/mtk.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(matches)} MTK mérkőzés elmentve.")
