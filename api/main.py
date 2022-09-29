from deta import Deta
import random
import string
from flask import Flask, jsonify, request, render_template
import os

from src.main import DividendModel



# deta = Deta(os.getenv("PROJECT_KEY"))

# users = deta.Base("users")

app = Flask(__name__)

API_V1 = "/api/v1"

@app.route("/model/<symbol>")
def index(symbol: str):
    try:
        amount = request.args.get("amount", 20_000, type=int)
        years = request.args.get("years", 10, type=int)

        dm = DividendModel(symbol)
        app.jinja_env.globals.update( 
            random_id=lambda: "".join(random.choice(string.ascii_letters) for i in range(8)).lower() 
        )
        return render_template(
            "index.html", 
            symbol = symbol.upper(),
            amount = amount,
            years = years,
            indicators = dm.get_indicators(amount),
            model_table = dm.get_model_table(amount, years),
            payout_ratio_table = dm.get_payout_ratio_table(),
        ), 200
    except Exception as err:
        raise err
        return jsonify({
            "status": "ERROR",
            "error": str(err)
        }), 500

@app.route(f"{API_V1}/historic-dividends/<symbol>")
def historic_dividends(symbol: str):
    try:
        dm = DividendModel(symbol)
        return jsonify({
            "status": "OK",
            "data": dm.get_dividends_per_year()
        }), 200
    except Exception as err:
        return jsonify({
            "status": "ERROR",
            "error": str(err)
        }), 500

@app.route(f"{API_V1}/historic-prices/<symbol>")
def historic_prices(symbol: str):
    try:
        dm = DividendModel(symbol)
        return jsonify({
            "status": "OK",
            "data": dm.get_prices_per_year()
        }), 200
    except Exception as err:
        raise err
        return jsonify({
            "status": "ERROR",
            "error": str(err)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)