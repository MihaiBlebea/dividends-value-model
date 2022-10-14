from src.utils import safeget
from src.yahoo_finance import YahooFinance


class Ticker:

    def __init__(self, symbol: str, yahoo_finance: YahooFinance = None)-> None:
        self.symbol = symbol
        self.yf = YahooFinance() if yahoo_finance is None else yahoo_finance

    def get_company_name(self)-> str:
        return safeget(self.yf.get_ticker_info(self.symbol), "quoteSummary", "result", 0, "quoteType", "shortName")

    def get_dividend_yield(self)-> float:
        return safeget(self.yf.get_ticker_info(self.symbol), "quoteSummary", "result", 0, "summaryDetail", "trailingAnnualDividendYield", "raw")

    def get_industry(self)-> str:
        return safeget(self.yf.get_ticker_info(self.symbol), "quoteSummary", "result", 0, "assetProfile", "industry")

    def get_sector(self)-> str:
        return safeget(self.yf.get_ticker_info(self.symbol), "quoteSummary", "result", 0, "assetProfile", "sector")
