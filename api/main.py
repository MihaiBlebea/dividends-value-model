import os
from flask import Flask, jsonify, render_template
from flask_login import (
    LoginManager,
    current_user,
)

from src.ticker import Ticker

from src.portfolio_repo import PortfolioRepo
from src.user import User
from src.utils import to_percentage, to_gbp_fmt, to_int, to_date

from api.controllers.user import login, login_callback, logout
from api.controllers.portfolio import (
    get_portfolio,
    add_symbol,
    set_amount,
    remove_symbol,
)


# Initiate the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

app.jinja_env.filters["to_percentage"] = to_percentage
app.jinja_env.filters["to_gbp_fmt"] = to_gbp_fmt
app.jinja_env.filters["to_int"] = to_int
app.jinja_env.filters["to_date"] = to_date

# Initiate the Flask login
login_manager = LoginManager()
login_manager.init_app(app)


API_V1 = "/api/v1"


@login_manager.user_loader
def load_user(user_id: str):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


app.add_url_rule("/login", methods=["GET"], view_func=login)

app.add_url_rule("/login/callback", methods=["GET"], view_func=login_callback)

app.add_url_rule("/logout", methods=["GET"], view_func=logout)


app.add_url_rule("/portfolio/<portfolio_id>", methods=["GET"], view_func=get_portfolio)

app.add_url_rule("/portfolio/add", methods=["POST"], view_func=add_symbol)

app.add_url_rule("/portfolio/amount", methods=["POST"], view_func=set_amount)

app.add_url_rule(
    "/portfolio/remove/<symbol>", methods=["POST"], view_func=remove_symbol
)


@app.route("/", methods=["GET"])
def index():
    try:
        if current_user.is_authenticated:

            repo = PortfolioRepo()
            portfolios = repo.find_with_user_id(current_user.id)
            [print(p.id) for p in portfolios]
            return render_template(
                "index.html",
                username=current_user.name,
                portfolios=[{"id": p.id} for p in portfolios],
            )
        else:
            return render_template("index.html")
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500


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
    app.run(debug=True, host="0.0.0.0", port=8080, ssl_context="adhoc")
