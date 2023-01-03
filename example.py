from src.ticker import Ticker
from src.portfolio_repo import PortfolioRepo
from src.portfolio import Portfolio
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()

    print(os.getenv("PYTHONHTTPSVERIFY"))

    o = Ticker("O")
    aapl = Ticker("AAPL")

    port = Portfolio([o, aapl])

    repo = PortfolioRepo()

    repo.save(port)

    # print(t.dividend_discount_model(0.08))
