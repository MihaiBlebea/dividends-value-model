from flask import Flask, jsonify, request
from src.dividend_indicator import DividendIndicator
from src.dividend_calculator import DividendCalculator
from src.ticker import Ticker


app = Flask(__name__)

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


@app.route(f"{API_V1}/dividends/<symbol>/future-earnings", methods=["GET"])
def get_future_earnings(symbol: str):
    try:
        args = request.args
        invest_amount = args.get("invest-amount", type=float, default=20_000)
        years = args.get("years", type=int, default=10)
        reinvest_dividends = args.get("reinvest-dividends", type=bool, default=True)
        reinvest_annualy = args.get("reinvest-annualy", type=bool, default=True)

        dc = DividendCalculator(symbol)
        result = dc.predict_future_earnings(
            invest_amount,
            years,
            reinvest_dividends,
            reinvest_annualy,
        )

        return jsonify({"status": "OK", "data": result}), 200
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/dividends-per-month", methods=["GET"])
def get_invest_for_dividend_per_month(symbol: str):
    try:
        args = request.args
        dividend_per_month = args.get("dividend-per-month", type=float, default=1_000)
        dc = DividendCalculator(symbol)
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": dc.invest_for_dividend_per_month(dividend_per_month),
                }
            ),
            200,
        )
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/years-till-recoup", methods=["GET"])
def get_years_till_recoup_investment(symbol: str):
    try:
        dc = DividendCalculator(symbol)
        return jsonify({"status": "OK", "data": dc.years_till_recoup_investment()}), 200
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/historic-per-year", methods=["GET"])
def get_historic_per_year(symbol: str):
    try:
        dc = DividendCalculator(symbol)
        return jsonify({"status": "OK", "data": dc.get_dividends_per_year()}), 200
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/dividends-for-investment", methods=["GET"])
def get_dividends_for_investment(symbol: str):
    try:
        args = request.args
        invest_amount = args.get("invest-amount", type=float, default=20_000)

        dc = DividendCalculator(symbol)
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": dc.dividends_for_amount_invested(invest_amount),
                }
            ),
            200,
        )
    except Exception as err:
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route(f"{API_V1}/dividends/<symbol>/indicators", methods=["GET"])
def get_indicators(symbol: str):
    try:
        dc = DividendCalculator(symbol)
        di = DividendIndicator(symbol)
        return (
            jsonify(
                {
                    "status": "OK",
                    "data": {
                        "dividend_yield": di.get_dividend_yield(),
                        "current_price": di.get_current_price(),
                        "current_dividend_amount": dc.current_year_div_per_share(),
                        "dividend_growth": dc.get_yearly_dividend_growth(5),
                        "dividend_ratios_per_year": di.get_yearly_ratios(),
                        "cadi": dc.get_cadi(),
                        "beta": di.get_beta(),
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
