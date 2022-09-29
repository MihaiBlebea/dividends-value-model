import requests as re
from datetime import datetime
from currency_converter import CurrencyConverter
from src.utils import cache_factory, safeget


class Ticker:

    default_currency: str = "GBP"

    def __init__(self)-> None:
        self.conv = CurrencyConverter()

    @cache_factory("./cache", "ticker", 60 * 60 * 24)
    def get_data(self, symbol: str)-> dict:
        res = re.get(
            f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=assetProfile,balanceSheetHistory,balanceSheetHistoryQuarterly,calendarEvents,cashflowStatementHistory,cashflowStatementHistoryQuarterly,defaultKeyStatistics,earnings,earningsHistory,earningsTrend,financialData,fundOwnership,incomeStatementHistory,incomeStatementHistoryQuarterly,indexTrend,industryTrend,insiderHolders,insiderTransactions,institutionOwnership,majorDirectHolders,majorHoldersBreakdown,netSharePurchaseActivity,price,quoteType,recommendationTrend,secFilings,sectorTrend,summaryDetail,summaryProfile,symbol,upgradeDowngradeHistory,fundProfile,topHoldings,fundPerformance",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"},
        )

        assert res.status_code == 200, f"Status code is {res.status_code}"

        return res.json()

    def get_currency(self, symbol: str)-> str:
        return safeget(self.get_data(symbol), "quoteSummary", "result", 0, "summaryDetail", "currency")

    def get_current_price(self, symbol: str)-> float:
        price = safeget(self.get_data(symbol), "quoteSummary", "result", 0, "price", "regularMarketPrice", "raw")
        currency = self.get_currency(symbol)

        if currency == "GBp":
            price = price / 100
            currency = "GBP"

        return price if currency is self.default_currency else self.conv.convert(price, currency, self.default_currency)

    def get_company_name(self, symbol: str)-> str:
        return safeget(self.get_data(symbol), "quoteSummary", "result", 0, "quoteType", "shortName")

    def get_dividend_yield(self, symbol: str)-> float:
        return safeget(self.get_data(symbol), "quoteSummary", "result", 0, "summaryDetail", "dividendYield", "raw")

    def get_payout_ratio_yearly(self, symbol: str)-> list:
        statements = safeget(self.get_data(symbol), "quoteSummary", "result", 0, "cashflowStatementHistory", "cashflowStatements")
    
        return [
            {
                "date": sts["endDate"]["fmt"],
                "year": datetime.fromtimestamp(sts["endDate"]["raw"]).year,
                "net_income": sts["netIncome"]["raw"],
                "dividends_paid": abs(sts["dividendsPaid"]["raw"]),
                "payout_ratio": abs(sts["dividendsPaid"]["raw"]) / sts["netIncome"]["raw"]
            } 
            for sts in statements
        ]

    def get_industry(self, symbol: str)-> str:
        return safeget(self.get_data(symbol), "quoteSummary", "result", 0, "assetProfile", "industry")

    def get_sector(self, symbol: str)-> str:
        return safeget(self.get_data(symbol), "quoteSummary", "result", 0, "assetProfile", "sector")
