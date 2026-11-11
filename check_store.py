import json
import os
import urllib.request

PACKAGE_ID = os.environ.get("PACKAGE_ID", "946114")  # 1TB OLED (verify, see README steps)
COUNTRY = os.environ.get("COUNTRY", "GB")
TOPIC = os.environ["NTFY_TOPIC"]

URL = (
    "https://api.steampowered.com/IPhysicalGoodsService/"
    "CheckInventoryAvailableByPackage/v1"
    f"?origin=https://store.steampowered.com&country_code={COUNTRY}&packageid={PACKAGE_ID}"
)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def notify(msg):
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=msg.encode(),
        headers={
            "Title": "Steam Deck OLED 1TB",
            "Priority": "urgent",
            "Click": "https://store.steampowered.com/steamdeck/",
        },
    )
    urllib.request.urlopen(req, timeout=20)


data = get(URL)
print(data)
if data.get("response", {}).get("inventory_available"):
    notify("1TB Steam Deck OLED is IN STOCK. Go!")
