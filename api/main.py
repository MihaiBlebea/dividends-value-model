import os
import json
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests as re

from src.ticker import Ticker
from src.portfolio import Portfolio
from src.portfolio_repo import PortfolioRepo
from src.user import User
from src.utils import to_percentage, to_gbp_fmt, to_int, to_date

# Initiate the auth constants
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

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

client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return re.get(GOOGLE_DISCOVERY_URL).json()


API_V1 = "/api/v1"


@login_manager.user_loader
def load_user(user_id: str):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


@app.route("/login", methods=["GET"])
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback", methods=["GET"])
def login_callback():
    try:
        # Get authorization code Google sent back to you
        code = request.args.get("code")
        print(code)
        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send request to get tokens! Yay tokens!
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = re.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens!
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Now that we have tokens (yay) let's find and hit URL
        # from Google that gives you user's profile information,
        # including their Google Profile Image and Email
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = re.get(uri, headers=headers, data=body)

        # We want to make sure their email is verified.
        # The user authenticated with Google, authorized our
        # app, and now we've verified their email through Google!
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        # Create a user in our db with the information provided
        # by Google
        user = User(
            id=unique_id, name=users_name, email=users_email, profile_pic=picture
        )

        print(user)

        # Doesn't exist? Add to database
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)

        # Begin user session by logging the user in
        login_user(user)

        # Send user back to homepage
        return redirect(url_for("index"))
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


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


@app.route("/portfolio/<portfolio_id>", methods=["GET"])
@login_required
def get_portfolio(portfolio_id: str):
    try:
        args = request.args
        amount = int(args.get("amount", default=1_000))

        symbols = args.get("symbols", default=None)

        if symbols is None:
            repo = PortfolioRepo()
            portfolio = repo.get(portfolio_id)
            assert portfolio is not None, "Portfolio not found"

            tickers = portfolio.tickers
        else:
            symbols = symbols.split(",")
            tickers = [Ticker(symbol) for symbol in symbols]
            portfolio = Portfolio(tickers, current_user.id, portfolio_id)

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
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@app.route("/portfolio/add", methods=["POST"])
@login_required
def add_symbol():
    args = request.args
    amount = int(args.get("amount")) if args.get("amount") is not None else 1_000
    symbols = (
        args.get("symbols").split(",")
        if args.get("symbols") is not None
        else ["ADM.L", "TSCO.L"]
    )

    symbol = request.form.get("symbol")
    portfolio_id = request.form.get("portfolio_id")
    assert symbol is not None, "Please provide a symbol"

    if symbol not in symbols:
        symbols.append(symbol)

    return redirect(
        url_for(
            "get_portfolio",
            portfolio_id=portfolio_id,
            amount=amount,
            symbols=",".join(symbols),
        )
    )


@app.route("/portfolio/amount", methods=["POST"])
@login_required
def set_amount():
    args = request.args
    amount = (
        int(request.form.get("amount")) if args.get("amount") is not None else 1_000
    )
    symbols = args.get("symbols", default=None)
    assert symbols is not None, "Please provide a symbol"

    portfolio_id = request.form.get("portfolio_id")

    return redirect(
        url_for(
            "get_portfolio",
            portfolio_id=portfolio_id,
            amount=amount,
            symbols=symbols,
        )
    )


@app.route("/portfolio/remove/<symbol>", methods=["POST"])
@login_required
def remove_symbol(symbol: str):
    try:
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

        portfolio_id = request.form.get("portfolio_id")

        return redirect(
            url_for(
                "get_portfolio",
                portfolio_id=portfolio_id,
                amount=amount,
                symbols=",".join(symbols),
            )
        )
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
