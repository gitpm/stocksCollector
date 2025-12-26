import requests
import time
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.write_api import SYNCHRONOUS

# ---------------- CONFIG ----------------
API_KEY = "HIER_IHREN_ALPHA_VANTAGE_KEY_EINTRAGEN"

SYMBOLS = ["AAPL", "MSFT", "SAP.DE"]

INFLUX_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "CVG1SDUL9FOWBCYV"
ORG = "DEV"
BUCKET = "stocks"
# ---------------------------------------

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

for symbol in SYMBOLS:
    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": API_KEY
        },
        timeout=30
    )

    payload = response.json()

    # ---------- Fehlerbehandlung ----------
    if "Time Series (Daily)" not in payload:
        print(f"[WARN] Keine Kursdaten für {symbol}: {payload}")
        time.sleep(15)
        continue

    series = payload["Time Series (Daily)"]

    # Nur letzten Handelstag schreiben (empfohlen)
    latest_date = max(series.keys())
    values = series[latest_date]

    point = (
        Point("stock_price")
        .tag("symbol", symbol)
        .field("open", float(values["1. open"]))
        .field("high", float(values["2. high"]))
        .field("low", float(values["3. low"]))
        .field("close", float(values["4. close"]))
        .field("volume", float(values["5. volume"]))
        .time(
            datetime.fromisoformat(latest_date)
            .replace(tzinfo=timezone.utc)
        )
    )

    write_api.write(bucket=BUCKET, record=point)
    print(f"[OK] {symbol} {latest_date}")

    # Alpha-Vantage-Rate-Limit einhalten
    time.sleep(15)

client.close()
