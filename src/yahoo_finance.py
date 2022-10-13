import requests as re
import time
from datetime import datetime
from src.utils import (
	cache_factory, 
	safeget, 
	to_GBP,
)


class YahooFinance:

	@cache_factory("./cache", "ticker", 60 * 60 * 24)
	def get_ticker_info(self, symbol: str)-> dict:
		res = re.get(
			f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=assetProfile,balanceSheetHistory,balanceSheetHistoryQuarterly,calendarEvents,cashflowStatementHistory,cashflowStatementHistoryQuarterly,defaultKeyStatistics,earnings,earningsHistory,earningsTrend,financialData,fundOwnership,incomeStatementHistory,incomeStatementHistoryQuarterly,indexTrend,industryTrend,insiderHolders,insiderTransactions,institutionOwnership,majorDirectHolders,majorHoldersBreakdown,netSharePurchaseActivity,price,quoteType,recommendationTrend,secFilings,sectorTrend,summaryDetail,summaryProfile,symbol,upgradeDowngradeHistory,fundProfile,topHoldings,fundPerformance",
			headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
		)

		assert res.status_code == 200, f"Status code is {res.status_code}"

		return res.json()

	@cache_factory("./cache", "dividends", 60 * 60 * 24)
	def get_historic_dividends(self, symbol: str)-> dict:
		url = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1=0&period2={timestamp}&interval={interval}&events=div"
		res = re.get(
			url.format(symbol=symbol, timestamp=int(time.time()), interval="1mo"), 
			headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
		)

		assert res.status_code == 200, f"Status code is {res.status_code}"

		body = res.json()
		raw = safeget(body, "chart", "result", 0, "events", "dividends")
		assert raw is not None, f"Company {symbol} is not paying dividends"

		def format_dividend(div: dict)-> dict:
			currency = safeget(body, "chart", "result", 0, "meta", "currency")
			amount = safeget(div, "amount")

			return {
				**div, 
				"datetime": datetime.fromtimestamp(div["date"]).strftime("%d-%m-%Y"),
				"amount": to_GBP(amount, currency),
			}

		return [ format_dividend(div) for div in list(raw.values()) ]

	@cache_factory("./cache", "prices", ttl_sec=60 * 60 * 24)
	def get_historic_prices(self, symbol: str, interval: str = "1mo")-> dict:
		url = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range={range}&interval={interval}"
		res = re.get(
			url.format(symbol=symbol, range="max", interval=interval), 
			headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
		)

		assert res.status_code == 200, f"Status code is {res.status_code}"

		body = safeget(res.json(), "chart", "result", 0)
		assert body is not None, "Body of the response is null"

		prices = []
		for i, t in enumerate(body["timestamp"]):
			prices.append({
				"timestamp": t,
				"date": datetime.fromtimestamp(t).strftime("%d-%m-%Y"),
				"open": safeget(body, "indicators", "quote", 0, "open", i),
				"close": safeget(body, "indicators", "quote", 0, "close", i),
				"high": safeget(body, "indicators", "quote", 0, "high", i),
				"low": safeget(body, "indicators", "quote", 0, "low", i),
				"volume": safeget(body, "indicators", "quote", 0, "volume", i),
			})

		return prices

	def get_currency(self, symbol: str)-> str:
		return safeget(self.get_ticker_info(symbol), "quoteSummary", "result", 0, "summaryDetail", "currency")

	def get_current_price(self, symbol: str)-> float:
		price = safeget(self.get_ticker_info(symbol), "quoteSummary", "result", 0, "price", "regularMarketPrice", "raw")

		return to_GBP(price,  self.get_currency(symbol))


if __name__ == "__main__":
	from pprint import pprint
	yf = YahooFinance()

	pprint(yf.get_ticker_info("AAPL"))
