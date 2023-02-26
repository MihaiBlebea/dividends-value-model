from flask import jsonify, render_template, request
from flask_login import (
    login_required,
)

from src.ticker import Ticker
from src.yahoo_finance import YahooFinance


@login_required
def get_ticker_info(symbol: str):
    try:
        t = Ticker(symbol, YahooFinance())
        return render_template(
            "ticker.html",
            symbol=symbol,
            ticker_data={
                "industry": t.get_industry(),
                "sector": t.get_sector(),
            },
        )
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500


def search_ticker():
    try:
        args = request.args
        query = str(args.get("query", default=None))
        assert query is not None, "Query is None"

        yf = YahooFinance()
        results = yf.search_ticker(query)

        return jsonify({"results": results})
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500
