from typing import Dict, List
from datetime import datetime
from math import floor

from numpy import sort
from src.yahoo_finance import YahooFinance
from src.utils import calc_percentage_diff


class DividendCalculator:

	def __init__(self, symbol: str, yahoo_finance: YahooFinance = None)-> None:
		self.symbol = symbol
		self.yf = YahooFinance() if yahoo_finance is None else yahoo_finance

	def get_dividends_per_year(self)-> Dict[int, float]:
		data = self.yf.get_historic_dividends(self.symbol)
		current_year = datetime.now().year
		dividends = {}
		for d in data:
			dt = datetime.fromtimestamp(d["date"])
			if dt.year == current_year:
				continue
				
			if dt.year not in dividends:
				dividends[dt.year] = 0

			dividends[dt.year] += d["amount"]

		return dividends

	def get_yearly_dividend_growth(self, last_years: int = None)-> float:
		dividends = list(self.get_dividends_per_year().values())

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

	def current_year_div_per_share(self)-> float:
		yearly_dividends = self.get_dividends_per_year()
		dividend_growth = self.get_yearly_dividend_growth(5)
		last_year_div_amount = list(yearly_dividends.values())[-1]

		return last_year_div_amount + (last_year_div_amount * dividend_growth)

	def predict_future_earnings(
		self, 
		invest_amount: float, 
		for_years: int, 
		reinvest_dividends: bool = True,
		reinvest_annualy: bool = True)-> Dict[str, List]:

		result = {
			"labels": ["Year", "Share Count", "Dividend Payout", "Dividend Growth", "Dividend per Month", "Total Invested", "Total Dividends", "Total Balance"],
			"data": []
		}

		current_year = datetime.now().year
		dividend_growth = self.get_yearly_dividend_growth(5)
		balance = invest_amount
		current_year_div_per_share = self.current_year_div_per_share()
		current_price = self.yf.get_current_price(self.symbol)

		total_invested = invest_amount
		total_dividends = 0

		for index in range(for_years):
			# start of the year
			if reinvest_annualy is True and index > 0:
				total_invested += invest_amount
				balance += invest_amount

			share_count = floor(balance / current_price)
			dividend_amount = share_count * current_year_div_per_share
			total_dividends += dividend_amount
			if reinvest_dividends is True:
				balance += dividend_amount

			# log info
			result["data"].append(
				[
					current_year + index,
					share_count, # Total share count
					dividend_amount, # Dividend payout for current year
					dividend_growth, # Dividend growth rate
					dividend_amount / 12, # Dividend per month
					total_invested, # Total invested
					total_dividends, # Total dividends received
					balance, # Total balance = invested + dividends
				]
			)

		return result

	def invest_for_dividend_per_month(self, dividend_per_month: float)-> float:
		current_year_div_per_share = self.current_year_div_per_share()
		current_price = self.yf.get_current_price(self.symbol)
		dividend_per_year = dividend_per_month * 12

		return dividend_per_year / current_year_div_per_share * current_price

	def years_till_recoup_investment(self)-> int:
		invested = 1_000
		dividends = 0
		years = 0

		dividend_growth = self.get_yearly_dividend_growth(5)
		current_year_div_per_share = self.current_year_div_per_share()
		current_price = self.yf.get_current_price(self.symbol)
		share_count = floor(invested / current_price)
		while invested > dividends:
			current_year_div_per_share += current_year_div_per_share * dividend_growth
			dividends += share_count * current_year_div_per_share
			years += 1

		return years

	def dividends_for_amount_invested(self, amount: float = 20_000)-> float:
		current_year_div_per_share = self.current_year_div_per_share()
		current_price = self.yf.get_current_price(self.symbol)

		return floor(amount / current_price) * current_year_div_per_share

	def get_cadi(self)-> int:
		divs = list(self.get_dividends_per_year().values())
		sorted_divs = list(sort(divs))
		cadi = 0

		for i in range(len(divs) - 1, -1, -1):
			if divs[i] == sorted_divs[i]:
				cadi += 1

		return cadi


if __name__ == "__main__":
	from pprint import pprint
	div_calc = DividendCalculator("AAPL")
	# res = div_calc.predict_future_earnings(20_000, 10, True, True)
	# res = div_calc.invest_for_dividend_per_month(1_000)

	res = div_calc.get_cadi()

	pprint(res)


