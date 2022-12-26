from datetime import datetime
from src.yahoo_finance import YahooFinance
from src.utils import safeget


class DividendIndicator:
    def __init__(self, symbol: str, yahoo_finance: YahooFinance = None) -> None:
        self.symbol = symbol
        self.yf = YahooFinance() if yahoo_finance is None else yahoo_finance

    def get_dividend_yield(self) -> float:
        data = self.yf.get_ticker_info(self.symbol)

        div_yield = safeget(
            data, "quoteSummary", "result", 0, "summaryDetail", "dividendYield", "raw"
        )

        return div_yield if div_yield is not None else 0

    def get_beta(self) -> float:
        data = self.yf.get_ticker_info(self.symbol)

        return safeget(
            data, "quoteSummary", "result", 0, "defaultKeyStatistics", "beta", "raw"
        )

    def get_market_cap(self) -> float:
        data = self.yf.get_ticker_info(self.symbol)

        return safeget(
            data,
            "quoteSummary",
            "result",
            0,
            "summaryDetail",
            "marketCap",
            "raw",
        )

    def get_pe_ratio(self) -> float:
        data = self.yf.get_ticker_info(self.symbol)

        return safeget(
            data,
            "quoteSummary",
            "result",
            0,
            "summaryDetail",
            "trailingPE",
            "raw",
        )

    def get_current_price(self) -> float:
        return self.yf.get_current_price(self.symbol)

    def get_yearly_ratios(self) -> list:
        data = self.yf.get_ticker_info(self.symbol)

        statements = safeget(
            data,
            "quoteSummary",
            "result",
            0,
            "cashflowStatementHistory",
            "cashflowStatements",
        )

        return [
            {
                "date": safeget(sts, "endDate", "fmt"),
                "year": datetime.fromtimestamp(safeget(sts, "endDate", "raw")).year,
                "net_income": safeget(sts, "netIncome", "raw"),
                "dividends_paid": abs(safeget(sts, "dividendsPaid", "raw")),
                "payout_ratio": abs(safeget(sts, "dividendsPaid", "raw"))
                / safeget(sts, "netIncome", "raw"),
                "dividend_cover": safeget(sts, "netIncome", "raw")
                / abs(safeget(sts, "dividendsPaid", "raw")),
            }
            for sts in statements
        ]
