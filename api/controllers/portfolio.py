from flask import jsonify, request, render_template, redirect, url_for
from flask_login import (
    current_user,
    login_required,
)

from src.ticker import Ticker
from src.portfolio import Portfolio
from src.portfolio_repo import PortfolioRepo


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
