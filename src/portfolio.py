from typing import List, Dict, Any
from src.ticker import Ticker
from datetime import datetime
import uuid


class Portfolio:
    def __init__(
        self, tickers: List[Ticker], user_id: str = None, id: str = None
    ) -> None:
        self.id = str(uuid.uuid4()) if id is None else id
        self.tickers = tickers
        self.user_id = user_id

    def get_average_dividend_yield(self) -> float:
        return sum([t.get_dividend_yield() for t in self.tickers]) / len(self.tickers)

    def get_average_market_cap(self) -> float:
        return sum([t.get_market_cap() for t in self.tickers]) / len(self.tickers)

    def get_average_pe(self) -> float:
        return sum([t.get_pe_ratio() for t in self.tickers]) / len(self.tickers)

    def get_average_eps(self) -> float:
        return sum([t.get_eps_ratio() for t in self.tickers]) / len(self.tickers)

    def get_average_beta(self) -> float:
        return sum([t.get_beta() for t in self.tickers]) / len(self.tickers)

    def get_average_cadi(self) -> float:
        return sum([t.get_cadi() for t in self.tickers]) / len(self.tickers)

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

    def to_list(self) -> list:
        return [t.symbol for t in self.tickers]
