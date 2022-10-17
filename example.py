from src.dividend_calculator import DividendCalculator
from src.dividend_indicator import DividendIndicator

if __name__ == "__main__":
	# dc = DividendCalculator("AAPL")

	# print(dc.dividend_discount_model())

	di = DividendIndicator("AAPL")

	print(di.get_beta())