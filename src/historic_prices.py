from datetime import datetime
import requests as re
from src.utils import cache_factory


class HistoricPrices:

    @cache_factory("./cache", "historic_prices", ttl_sec=60 * 60 * 24)
    def get_data(self, symbol: str, interval: str = "1mo")-> dict:
        url = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}"
        res = re.get(
            url.format(symbol=symbol, range="max", interval=interval), 
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
        )

        assert res.status_code == 200, f"Status code is {res.status_code}"

        body = res.json()["chart"]["result"][0]

        prices = []
        for i, t in enumerate(body["timestamp"]):
            prices.append({
                "timestamp": t,
                "date": datetime.fromtimestamp(t).strftime("%d-%m-%Y"),
                "open": body["indicators"]["quote"][0]["open"][i],
                "close": body["indicators"]["quote"][0]["close"][i],
                "high": body["indicators"]["quote"][0]["high"][i],
                "low": body["indicators"]["quote"][0]["low"][i],
                "volume": body["indicators"]["quote"][0]["volume"][i]
            })

        return prices

    def group_per_year(self, symbol: str)-> dict:
        data = self.get_data(symbol, "3mo")
        result = {}
        for d in data:
            year = datetime.fromtimestamp(d["timestamp"]).year

            result[year] = d

        return result