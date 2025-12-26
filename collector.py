import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.write_api import SYNCHRONOUS
from datetime import datetime

API_KEY = "<ALPHA_VANTAGE_KEY>"
SYMBOLS = ["AAPL", "MSFT", "SAP.DE"]

INFLUX_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com/orgs/b6f47b8d112fc919"
INFLUX_TOKEN = "CVG1SDUL9FOWBCYV"
ORG = "DEV"
BUCKET = "stocks"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

for symbol in SYMBOLS:
    r = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": API_KEY
        }
    )
    data = r.json()["Time Series (Daily)"]

    for date, values in data.items():
        point = (
            Point("stock_price")
            .tag("symbol", symbol)
            .field("open", float(values["1. open"]))
            .field("high", float(values["2. high"]))
            .field("low", float(values["3. low"]))
            .field("close", float(values["4. close"]))
            .field("volume", float(values["5. volume"]))
            .time(datetime.fromisoformat(date))
        )
        write_api.write(bucket=BUCKET, record=point)
