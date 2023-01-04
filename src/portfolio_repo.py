from typing import List
import os
from deta import Deta
from src.portfolio import Portfolio
from src.ticker import Ticker


class PortfolioRepo:
    def __init__(self) -> None:
        self.portfolio_table = Deta(os.getenv("DETA_PROJECT_KEY")).Base("portfolios")

    def save(self, portfolio: Portfolio) -> None:
        self.portfolio_table.put(
            data={"symbols": portfolio.to_list(), "user_id": portfolio.user_id},
            key=portfolio.id,
        )

    def get(self, id: str) -> Portfolio:
        item = self.portfolio_table.get(id)
        if item is None:
            return None

        return Portfolio([Ticker(s) for s in item["symbols"]], item["user_id"], id)

    def find_with_user_id(self, user_id: str) -> List[Portfolio]:
        resp = self.portfolio_table.fetch({"user_id": user_id})
        if len(resp.items) == 0:
            return []

        return [
            Portfolio(
                [Ticker(s) for s in item["symbols"]], item["user_id"], str(item["key"])
            )
            for item in resp.items
        ]
