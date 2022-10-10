import json
from src.yahoo_finance import YahooFinance


class YahooFinanceStub(YahooFinance):

	def get_ticker_info(self, symbol: str)-> dict:
		with open("./src/tests/ticker_AAPL.json", "r") as file:
			return json.loads(file.read())

	def get_historic_dividends(self, symbol: str)-> dict:
		with open("./src/tests/dividends_AAPL.json", "r") as file:
			return json.loads(file.read())

	def get_historic_prices(self, symbol: str, interval: str = "1mo")-> dict:
		with open("./src/tests/prices_AAPL.json", "r") as file:
			return json.loads(file.read())