import base64
import os
import urllib.parse
import urllib.request

PACKAGE_ID = int(os.environ.get("PACKAGE_ID", "1202547"))  # 1TB OLED
COUNTRY = os.environ.get("COUNTRY", "GB")
TOPIC = os.environ["NTFY_TOPIC"]


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def encode(package_id, country):
    c = country.encode()
    raw = b"\x08" + varint(package_id) + b"\x12" + bytes([len(c)]) + c
    return base64.b64encode(raw).decode()


def in_stock():
    url = (
        "https://api.steampowered.com/IPhysicalGoodsService/"
        "CheckInventoryAvailableByPackage/v1?origin=https://store.steampowered.com"
        "&input_protobuf_encoded=" + urllib.parse.quote(encode(PACKAGE_ID, COUNTRY))
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    print("Response bytes:", data.hex(" "))
    if data.startswith(b"\x08\x01"):
        return True
    if data.startswith(b"\x08\x00"):
        return False
    raise RuntimeError("Unexpected response")


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


if __name__ == "__main__":
    if in_stock():
        notify("1TB Steam Deck OLED is IN STOCK. Go!")
    else:
        print("Out of stock")
