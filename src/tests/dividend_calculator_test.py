import unittest
from datetime import datetime
from src.dividend_calculator import DividendCalculator
from src.tests.yahoo_finance_stub import YahooFinanceStub


class TestDividendCalculator(unittest.TestCase):

	current_year = datetime.now().year

	yahoo_finance_stub = YahooFinanceStub()

	def test_no_reinvestment(self):
		"""
		Test that we get the right amount without any reinvestments
		"""

		dc = DividendCalculator("AAPL", self.yahoo_finance_stub)
		res = dc.predict_future_earnings(20_000, 10, False, False)

		data = res["data"]

		# First year
		self.assertEqual(
			data[0][0], 
			self.current_year, 
			f"The first year is incorrect, expected {self.current_year}, got {data[0][0]}",
		)
		self.assertEqual(
			data[0][1], 
			142, 
			f"The number of shares is incorrect, expected 142, got {data[0][1]}",
		)
		self.assertEqual(
			data[0][2], 
			130.826233, 
			f"The dividend payout is incorrect, expected 130.826233, got {data[0][2]}",
		)
		self.assertEqual(
			data[0][3], 
			0.0651, 
			f"The monthly dividend payout is incorrect, expected 0.0651, got {data[0][3]}",
		)
		self.assertEqual(
			data[0][4], 
			10.9021860833333333, 
			f"The monthly dividend payout is incorrect, expected 10.902186083333333, got {data[0][4]}",
		)
		self.assertEqual(
			data[0][5], 
			20_000, 
			f"Total invested amount is incorrect, expected 20_000, got {data[0][5]}",
		)
		self.assertEqual(
			data[0][6], 
			130.826233, 
			f"Total dividend amount incorrect, expected 130.826233, got {data[0][6]}",
		)
		self.assertEqual(
			data[0][7], 
			20_000, 
			f"Total balance amount is incorrect, expected 20_000, got {data[0][7]}",
		)

		# Last year
		self.assertEqual(
			data[-1][0], 
			self.current_year + 9, 
			f"The first year is incorrect, expected {self.current_year + 10}, got {data[-1][0]}",
		)
		self.assertEqual(
			data[-1][1], 
			142, 
			f"The number of shares is incorrect, expected 142, got {data[-1][1]}",
		)
		self.assertEqual(
			data[-1][2], 
			130.826233, 
			f"The dividend payout is incorrect, expected 130.826233, got {data[-1][2]}",
		)
		self.assertEqual(
			data[-1][4], 
			10.9021860833333333, 
			f"The monthly dividend payout is incorrect, expected 10.902186083333333, got {data[-1][4]}",
		)
		self.assertEqual(
			data[-1][5], 
			20_000, 
			f"Total invested amount is incorrect, expected 20_000, got {data[-1][5]}",
		)
		self.assertEqual(
			data[-1][6], 
			1308.26233, 
			f"Total dividend amount incorrect, expected 130.826233, got {data[-1][6]}",
		)
		self.assertEqual(
			data[-1][7], 
			20_000, 
			f"Total balance amount is incorrect, expected 20_000, got {data[-1][7]}",
		)

	def test_reinvest_annualy(self):
		"""
		Test that we get the right result if twe reinvest the same amount every year
		"""

		dc = DividendCalculator("AAPL", self.yahoo_finance_stub)
		res = dc.predict_future_earnings(20_000, 10, False)

		data = res["data"]

		# Check data in last year
		self.assertEqual(
			data[-1][0], 
			self.current_year + 9, 
			f"The first year is incorrect, expected {self.current_year + 10}, got {data[-1][0]}",
		)
		self.assertEqual(
			data[-1][1], 
			1427, 
			f"The number of shares is incorrect, expected 1427, got {data[-1][1]}",
		)
		self.assertEqual(
			data[-1][2], 
			1314.7115105, 
			f"The dividend payout is incorrect, expected 1314.7115105, got {data[-1][2]}",
		)
		self.assertEqual(
			data[-1][4], 
			109.55929254166666, 
			f"The monthly dividend payout is incorrect, expected 109.55929254166666, got {data[-1][4]}",
		)
		self.assertEqual(
			data[-1][5], 
			200_000, 
			f"Total invested amount is incorrect, expected 200_000, got {data[-1][5]}",
		)
		self.assertEqual(
			data[-1][6], 
			7229.531340500001, 
			f"Total dividend amount incorrect, expected 7229.531340500001, got {data[-1][6]}",
		)
		self.assertEqual(
			data[-1][7], 
			200_000, 
			f"Total balance amount is incorrect, expected 200_000, got {data[-1][7]}",
		)

	def test_reinvest_dividends(self):
		"""
		Test that we get the right result if twe reinvest the same amount every year
		"""

		dc = DividendCalculator("AAPL", self.yahoo_finance_stub)
		res = dc.predict_future_earnings(20_000, 10)

		data = res["data"]

		# Check data in last year
		self.assertEqual(
			data[-1][0], 
			self.current_year + 9, 
			f"The first year is incorrect, expected {self.current_year + 10}, got {data[-1][0]}",
		)
		self.assertEqual(
			data[-1][1], 
			1470, 
			f"The number of shares is incorrect, expected 1470, got {data[-1][1]}",
		)
		self.assertEqual(
			data[-1][2], 
			1354.3279049999999, 
			f"The dividend payout is incorrect, expected 1354.3279049999999, got {data[-1][2]}",
		)
		self.assertEqual(
			data[-1][4], 
			112.86065874999998, 
			f"The monthly dividend payout is incorrect, expected 112.86065874999998, got {data[-1][4]}",
		)
		self.assertEqual(
			data[-1][5], 
			200_000, 
			f"Total invested amount is incorrect, expected 200_000, got {data[-1][5]}",
		)
		self.assertEqual(
			data[-1][6], 
			7374.177246, 
			f"Total dividend amount incorrect, expected 7374.177246, got {data[-1][6]}",
		)
		self.assertEqual(
			data[-1][7], 
			207374.17724600004, 
			f"Total balance amount is incorrect, expected 207374.17724600004, got {data[-1][7]}",
		)

if __name__ == "__main__":
    unittest.main()