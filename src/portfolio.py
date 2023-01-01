from typing import List, Dict, Any
from src.ticker import Ticker
from datetime import datetime


class Portfolio:
    def __init__(self, tickers: List[Ticker]) -> None:
        self.tickers = tickers

    def get_average_dividend_yield(self) -> float:
        return sum([t.get_dividend_yield() for t in self.tickers]) / len(self.tickers)

    def project(self, years: int, invest_per_year: int) -> List[Dict[str, Any]]:
        result = []

        current_year = int(datetime.now().strftime("%Y"))
        end_of_year = 0

        for year in range(years):
            start_of_year = invest_per_year + end_of_year
            end_of_year = (
                start_of_year + start_of_year * self.get_average_dividend_yield()
            )

            dividend_per_year = end_of_year - start_of_year
            result.append(
                {
                    "year": current_year + year,
                    "invest_per_year": invest_per_year,
                    "start_of_year": start_of_year,
                    "end_of_year": end_of_year,
                    "dividend_per_year": dividend_per_year,
                    "dividend_per_month": dividend_per_year / 12,
                }
            )

        return result
