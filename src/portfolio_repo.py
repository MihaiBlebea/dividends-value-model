import os
from deta import Deta
from src.portfolio import Portfolio


class PortfolioRepo:
    def __init__(self) -> None:
        self.portfolio_table = Deta(os.getenv("DETA_PROJECT_KEY")).Base("portfolios")

    def save(self, portfolio: Portfolio) -> None:
        self.portfolio_table.put(data=portfolio.to_list(), key=portfolio.id)

    def get(self, id: str) -> Portfolio:
        item = self.portfolio_table.get(id)

        return Portfolio(item.value, item.id)
