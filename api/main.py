from flask import Flask, jsonify, request, render_template, redirect
from src.ticker import Ticker
from src.portfolio import Portfolio
from src.portfolio_repo import PortfolioRepo
from src.utils import to_percentage, to_gbp_fmt, to_int, to_date


app = Flask(__name__)
app.jinja_env.filters["to_percentage"] = to_percentage
app.jinja_env.filters["to_gbp_fmt"] = to_gbp_fmt
app.jinja_env.filters["to_int"] = to_int
app.jinja_env.filters["to_date"] = to_date


API_V1 = "/api/v1"


@app.route("/", methods=["GET"])
def index():
    try:
        host = request.host_url.rstrip("/")
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": [
                        f"{host}{API_V1}/dividends/AAPL/future-earnings",
                        f"{host}{API_V1}/dividends/AAPL/dividends-per-month",
                        f"{host}{API_V1}/dividends/AAPL/years-till-recoup",
                        f"{host}{API_V1}/dividends/AAPL/historic-per-year",
                        f"{host}{API_V1}/dividends/AAPL/dividends-for-investment",
                        f"{host}{API_V1}/dividends/AAPL/indicators",
                        f"{host}{API_V1}/dividends/AAPL/company-basics",
                    ],
                }
            ),
            200,
        )
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route("/webapp/<portfolio_id>", methods=["GET"])
def get_portfolio(portfolio_id: str):
    args = request.args
    amount = int(args.get("amount", default=1_000))

    symbols = args.get("symbols", default=None)

    if symbols is None:
        repo = PortfolioRepo()
        portfolio = repo.get(portfolio_id)
        tickers = portfolio.tickers
    else:
        symbols = symbols.split(",")
        tickers = [Ticker(symbol) for symbol in symbols]
        portfolio = Portfolio(tickers, portfolio_id)

        repo = PortfolioRepo()
        repo.save(portfolio)

    total_market_cap = sum([t.get_market_cap() for t in tickers])
    total_div_yield = sum([t.get_dividend_yield() for t in tickers])

    stocks = [
        {
            "symbol": t.symbol,
            "company_name": t.get_company_name(),
            "industry": t.get_industry(),
            "sector": t.get_sector(),
            "dividend_yield": t.get_dividend_yield(),
            "current_price": t.get_current_price(),
            "current_dividend_amount": t.current_year_div_per_share(),
            "dividend_growth": t.get_yearly_dividend_growth(5),
            "trailing_average_div_yield": t.get_trailing_average_div_yield(),
            "dividend_ratios_per_year": t.get_yearly_ratios(),
            "cadi": t.get_cadi(),
            "beta": t.get_beta(),
            "pe_ratio": t.get_pe_ratio(),
            "eps_ratio": t.get_eps_ratio(),
            "market_cap": t.get_market_cap(),
            "equal_weight": (100 / len(tickers) / 100),
            "market_cap_weight": (t.get_market_cap() / total_market_cap),
            "div_yield_weight": (t.get_dividend_yield() / total_div_yield),
            "ex_dividend_date": t.get_ex_dividend_date(),
            "dividend_date": t.get_next_dividend_date(),
        }
        for t in tickers
    ]
    return render_template(
        "portfolio.html",
        amount=amount,
        portfolio_id=portfolio_id,
        stocks=stocks,
        portfolio={
            "average_dividend_yield": portfolio.get_average_dividend_yield(),
            "average_market_cap": portfolio.get_average_market_cap(),
            "average_pe": portfolio.get_average_pe(),
            "average_eps": portfolio.get_average_eps(),
            "average_beta": portfolio.get_average_beta(),
            "average_cadi": portfolio.get_average_cadi(),
        },
        projections=portfolio.project(22, amount),
    )


@app.route("/webapp/portfolio/add", methods=["POST"])
def add_symbol():
    args = request.args
    amount = int(args.get("amount")) if args.get("amount") is not None else 1_000
    symbols = (
        args.get("symbols").split(",")
        if args.get("symbols") is not None
        else ["ADM.L", "TSCO.L"]
    )

    symbol = request.form.get("symbol")
    assert symbol is not None, "Please provide a symbol"

    if symbol not in symbols:
        symbols.append(symbol)

    return redirect(
        f"/webapp/1234?amount={amount}&symbols=" + ",".join(symbols), code=302
    )


@app.route("/webapp/portfolio/amount", methods=["POST"])
def set_amount():
    args = request.args
    amount = (
        int(request.form.get("amount")) if args.get("amount") is not None else 1_000
    )
    symbols = (
        args.get("symbols") if args.get("symbols") is not None else ["ADM.L", "TSCO.L"]
    )

    return redirect(f"/webapp/1234?amount={amount}&symbols={symbols}", code=302)


@app.route("/webapp/portfolio/remove/<symbol>", methods=["POST"])
def remove_symbol(symbol: str):
    args = request.args
    amount = int(args.get("amount")) if args.get("amount") is not None else 1_000
    symbols = (
        args.get("symbols").split(",")
        if args.get("symbols") is not None
        else ["ADM.L", "TSCO.L"]
    )

    assert len(symbols) > 1, "Portfolio must have at least one stock"

    if symbol in symbols:
        symbols.remove(symbol)

    return redirect(
        f"/webapp/1234?amount={amount}&symbols=" + ",".join(symbols), code=302
    )


@app.route(f"{API_V1}/dividends/<symbol>/historic-per-year", methods=["GET"])
def get_historic_per_year(symbol: str):
    try:
        t = Ticker(symbol)
        return jsonify({"status": "OK", "data": t.get_dividends_per_year()}), 200
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/indicators", methods=["GET"])
def get_indicators(symbol: str):
    try:
        t = Ticker(symbol)
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": {
                        "dividend_yield": t.get_dividend_yield(),
                        "current_price": t.get_current_price(),
                        "current_dividend_amount": t.current_year_div_per_share(),
                        "dividend_growth": t.get_yearly_dividend_growth(5),
                        "dividend_ratios_per_year": t.get_yearly_ratios(),
                        "cadi": t.get_cadi(),
                        "beta": t.get_beta(),
                        "pe_ratio": t.get_pe_ratio(),
                        "eps_ratio": t.get_eps_ratio(),
                        "market_cap": t.get_market_cap(),
                    },
                }
            ),
            200,
        )
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/company-basics", methods=["GET"])
def get_company_basics(symbol: str):
    try:
        t = Ticker(symbol)
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": {
                        "company_name": t.get_company_name(),
                        "industry": t.get_industry(),
                        "sector": t.get_sector(),
                    },
                }
            ),
            200,
        )
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
