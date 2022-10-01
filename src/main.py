from typing import Dict, List
import argparse
from math import floor
from datetime import datetime
from src.historic_prices import HistoricPrices
from src.historic_dividends import HistoricDividends
from src.ticker import Ticker
from src.utils import (
	growth_in_percentage,
	calc_percentage_diff, 
)
from pprint import pprint


class DividendModel:

	def __init__(self, symbol: str)-> None:
		self.symbol = symbol.upper()
		self.ticker = Ticker()
		self.historic_dividends = HistoricDividends()
		self.historic_prices = HistoricPrices()

		self.divs_per_year = self.historic_dividends.group_per_year(self.symbol)
		self.yearly_growth = self.historic_dividends.yearly_growth(self.symbol, 5)
		self.company_name = self.ticker.get_company_name(self.symbol)
		self.div_yield = self.ticker.get_dividend_yield(self.symbol)
		self.current_price = self.ticker.get_current_price(self.symbol)
		self.last_div_paid = list(self.divs_per_year.values())[-1]

	def get_indicators(self, amount: float)-> Dict[str, str]:
		qty = floor(amount / self.current_price)
		dividends = qty * self.last_div_paid

		return {
			"amount_invested": {
				"fmt": f"£{amount:,}",
				"raw": amount,
			},
			"stock_quantity": {
				"fmt": f"{qty} stocks",
				"raw": qty,
			},
			"company_name": f"{self.company_name} ({self.symbol})",
			"industry": self.ticker.get_industry(self.symbol),
			"sector": self.ticker.get_sector(self.symbol),
			"dividends_received": {
				"fmt": f"£{round(dividends, 2):,}",
				"raw": dividends,
			},
			"dividend_yield": {
				"fmt": f"{round(self.div_yield * 100, 2)}%",
				"raw": self.div_yield,
			},
			"current_stock_price": {
				"fmt": f"£{round(self.current_price, 2):,}",
				"raw": self.current_price,
			},
			"dividend_per_stock": {
				"fmt": f"£{round(self.last_div_paid, 2):,}",
				"raw": self.last_div_paid,
			},
			"average_dividend_yearly_growth": {
				"fmt": f"{round(self.yearly_growth * 100, 2)}%",
				"raw": self.yearly_growth,
			},
			"dividend_length": {
				"fmt": f"{len(self.divs_per_year)} years",
				"raw": len(self.divs_per_year),
			}
		}

	def get_model_table(self, amount: float, years: int)-> Dict[str, List]:
		result ={
			"labels": ["Year", "Stocks", "Dividend per Year", "Dividends", "Yield per Month", "Total Invested", "Balance"],
			"data": []
		}
		current_year = datetime.now().year

		last_dividend = self.last_div_paid
		balance = amount
		total_invested = 0
		for y in range(years):
			qty = floor(balance / self.current_price)
			div_amount = qty * last_dividend
			balance += div_amount
			total_invested += amount
			result["data"].append([
				str(current_year + y), 
				str(qty), 
				f"£{round(last_dividend, 3)}", 
				f"£{round(div_amount, 2):,}", 
				f"£{round(div_amount / 12, 2):,}", 
				f"£{round(total_invested, 2):,}",
				f"£{round(balance, 2):,}",
			])
			
			last_dividend = last_dividend + (last_dividend * self.yearly_growth)
			balance += amount
		
		return result

	def get_payout_ratio_table(self)-> Dict[str, List]:
		result ={
			"labels": ["Year", "Net Income", "Dividends Paid", "Payout Ratio"],
			"data": []
		}

		for pr in self.ticker.get_payout_ratio_yearly(self.symbol):
			net_income = pr["net_income"]
			dividends_paid = pr["dividends_paid"]
			payout_ratio = round(pr["payout_ratio"] * 100, 2)
			result["data"].append([
				str(pr["year"]), 
				f"£{net_income:,}", 
				f"£{dividends_paid:,}", 
				payout_ratio,
			])

		return result

	def get_dividends_per_year(self)-> List[dict]:
		div_amounts = list(self.divs_per_year.values())
		growth = growth_in_percentage(div_amounts)
		
		return [
			{
				"year": d,
				"amount": div_amounts[i],
				"growth": growth[i]
			}
			for i, d in enumerate(self.divs_per_year)
		]

	def get_prices_per_year(self)-> List[dict]:
		data = self.historic_prices.group_per_year(self.symbol)

		prices = [
			d["close"] for d in list(data.values()) if d["close"] is not None
		]
		growth = growth_in_percentage(prices)
		years = list(data.keys())

		return [
			{
				"year": years[i],
				"price": price,
				"growth": growth[i]
			}
			for i, price in enumerate(prices)
		]

	def get_dividend_yield_per_year(self):
		dividends = self.get_dividends_per_year()

		div_dict = {}
		for div in dividends:
			div_dict[div["year"]] = {
				"dividend": div["amount"],
				"dividend_growth": div["growth"],
			}
	
		result = []
		for p in self.get_prices_per_year():
			year = p["year"]
			dividend = round(div_dict[year]["dividend"], 4) if year in div_dict else 0
			price = p["price"]
			data = {
				"price": round(price, 4),
				"year": year,
				"price_growth": round(p["growth"], 4),
				"dividend": dividend,
				"dividend_growth": round(div_dict[year]["dividend_growth"], 4) if year in div_dict else 0,
				"dividend_yield": round(dividend / price, 4) if dividend != 0 else 0,
			}

			result.append(data)

		return result

	def get_dividend_yield_table(self)-> Dict[str, List]:
		result ={
			"labels": ["Year", "Price", "Dividend Paid", "Dividend Yield"],
			"data": []
		}

		for div in self.get_dividend_yield_per_year():
			price = div["price"]
			dividend = div["dividend"]
			div_yield = div["dividend_yield"]
			result["data"].append([
				str(div["year"]), 
				f"£{price:,}", 
				f"£{dividend:,}", 
				f"{round(div_yield * 100, 2)}%"
			])

		return result

if __name__ == "__main__":
	parser = argparse.ArgumentParser("dividend calculator", description="Add some integers.")
	parser.add_argument("-s", "--symbol", required=True, type=str, help="symbol of the ticker")
	parser.add_argument("-a", "--amount", required=True, type=float, help="amount to invest in GBP")
	parser.add_argument("-y", "--years", required=False, default=None, type=int, help="number of years of investment")
	
	args = parser.parse_args()

	symbol = args.symbol.upper()
	amount = args.amount
	years = args.years

	dm = DividendModel(symbol)

	pprint(dm.get_indicators(amount))
	pprint(dm.get_model_table(amount, years))
	pprint(dm.get_payout_ratio_table())
