import os
import urllib.request

from playwright.sync_api import sync_playwright

TOPIC = os.environ["NTFY_TOPIC"]
URL = "https://store.steampowered.com/steamdeck/?cc=GB"

# For every "Out of stock" / "Add to cart" button, walk up to the nearest
# container that mentions 1TB (and not 512GB) and report the button text.
JS = """
() => {
  const out = [];
  const els = [...document.querySelectorAll('a,button,div,span')];
  for (const el of els) {
    const t = (el.innerText || '').trim();
    if (t !== 'Out of stock' && !/^add to cart$/i.test(t)) continue;
    let p = el;
    while (p && !(p.innerText || '').includes('1TB')) p = p.parentElement;
    if (p && !(p.innerText || '').includes('512GB')) out.push(t);
  }
  return out;
}
"""


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


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(locale="en-GB")
    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    text = page.inner_text("body")
    found = page.evaluate(JS)
    browser.close()

print("Prices on page:", [w for w in text.split() if w[:1] in "£$€"][:6])
print("1TB button states:", found)

if any(s.lower() == "add to cart" for s in found):
    notify("1TB Steam Deck OLED is IN STOCK. Go!")
elif found:
    print("Out of stock")
else:
    print("Could not find the 1TB button. Page text:")
    print(text[:1500])
    raise SystemExit(1)
