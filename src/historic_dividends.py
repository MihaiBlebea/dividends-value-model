import requests as re
from datetime import datetime
import time
from currency_converter import CurrencyConverter
from src.utils import (
	cache_factory, safeget, calc_percentage_diff
)


class HistoricDividends:

	default_currency: str = "GBP"

	def __init__(self)-> None:
		self.conv = CurrencyConverter()

	@cache_factory("./cache", "dividends", 60 * 60 * 24)
	def get_data(self, symbol: str)-> dict:
		url = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1=0&period2={timestamp}&interval={interval}&events=div"
		res = re.get(
			url.format(symbol=symbol, timestamp=int(time.time()), interval="1mo"), 
			headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
		)

		assert res.status_code == 200, f"Status code is {res.status_code}"

		body = res.json()
		raw = safeget(body, "chart", "result", 0, "events", "dividends")
		if raw is None:
			raise Exception(f"Company {symbol} is not paying dividends")

		currency = safeget(body, "chart", "result", 0, "meta", "currency")
		if currency is None:
			raise Exception("Currency is unknown")
		
		return [
			{
				**div, 
				"datetime": datetime.fromtimestamp(div["date"]).strftime("%d-%m-%Y"),
				"amount": self._calc_real_amount(div["amount"], currency)
			} 
			for div in
			list(raw.values())
		]

	def group_per_year(self, symbol: str)-> dict:
		data = self.get_data(symbol)
		current_year = datetime.now().year
		first_year = datetime.fromtimestamp(data[0]["date"]).year
		dividends = {}
		for d in data:
			dt = datetime.fromtimestamp(d["date"])
			if dt.year == current_year:
				continue

			if dt.year < first_year:
				continue
				
			if dt.year not in dividends:
				dividends[dt.year] = 0

			dividends[dt.year] += d["amount"]

		return dividends

	def yearly_growth(self, symbol: str, last_years: int = None)-> float:
		dividends = list(self.group_per_year(symbol).values())

		if last_years is not None:
			dividends = dividends[-last_years:]
		initial = None
		total_growth = 0
		for i, div in enumerate(dividends):
			if i == 0:
				initial = div
				continue

			total_growth += calc_percentage_diff(initial, div)

			initial = div

		return round(total_growth / len(dividends), 4)

	def _calc_real_amount(self, amount: float, currency: str)-> float:
		if currency == "GBp":
			amount = amount / 100
			currency = "GBP"
		amount = amount if currency is self.default_currency else self.conv.convert(amount, currency, self.default_currency)
		if currency == "USD":
			amount -= (amount * 0.15)

		return amount

