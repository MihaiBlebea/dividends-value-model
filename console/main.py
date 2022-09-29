import argparse
from datetime import datetime
from time import sleep
from src.historic_dividends import HistoricDividends
from src.ticker import Ticker
from rich.console import Console
from rich.table import Table
from rich.progress import track


def show_growth(last_dividend: float, yearly_growth: float, initial_amount: float, years: int):
    ticker = Ticker()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Year", justify="center")
    table.add_column("Stocks", justify="center")
    table.add_column("Dividend per Year", justify="center")
    table.add_column("Dividends", justify="left")
    table.add_column("Yield per Month", justify="left")
    table.add_column("Total Invested", justify="left")
    table.add_column("Balance", justify="left")

    current_year = datetime.now().year

    amount = initial_amount
    total_invested = 0
    for y in range(years):
        qty = ticker.buy_quantity(symbol, amount)
        div_amount = qty * last_dividend
        amount += div_amount
        total_invested += initial_amount
        table.add_row(
            str(current_year + y), 
            str(qty), 
            f"£{round(last_dividend, 3)}", 
            f"£{round(div_amount, 2):,}", 
            f"£{round(div_amount / 12, 2):,}", 
            f"£{round(total_invested, 2):,}",
            f"£{round(amount, 2):,}",
        )
        
        last_dividend = last_dividend + (last_dividend * yearly_growth)
        amount += initial_amount

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("dividend calculator", description="Add some integers.")
    parser.add_argument("-s", "--symbol", required=True, type=str, help="symbol of the ticker")
    parser.add_argument("-a", "--amount", required=True, type=float, help="amount to invest in GBP")
    parser.add_argument("-y", "--years", required=False, default=None, type=int, help="number of years of investment")
    
    args = parser.parse_args()

    symbol = args.symbol.upper()
    amount = args.amount
    years = args.years

    hdiv = HistoricDividends()

    divs = hdiv.group_per_year(symbol)
    yearly_growth = hdiv.yearly_growth(symbol, 5)

    ticker = Ticker()
    company = ticker.get_company_name(symbol)
    div_yield = ticker.get_dividend_yield(symbol)
    current_price = ticker.get_current_price(symbol)

    last_div = list(divs.values())[-1]
    qty = ticker.buy_quantity(symbol, amount)
    div = qty * last_div

    for step in track(range(100), description=f"Getting {symbol} data"):
        sleep(0.01)

    console = Console()
    console.print(f"\n:white_check_mark: If you invested [bold cyan]£{amount:,}[/bold cyan] last year in [bold white]{company} ({symbol})[/bold white], you would have received [bold cyan]£{round(div, 2):,}[/bold cyan] in dividends.\n")

    console.print(f":white_check_mark: Dividend yield is [bold cyan]{round(div_yield * 100, 2)}%[/bold cyan].\n")

    console.print(f":white_check_mark: Current stock price is [bold cyan]£{round(current_price, 2):,}[/bold cyan].\n")

    console.print(f":white_check_mark: Company had a dividend of [bold cyan]£{round(last_div, 2):,}/stock[/bold cyan] last year.\n")

    console.print(f":white_check_mark: Average dividend growth is [bold cyan]{round(yearly_growth * 100, 2)}%[/bold cyan] per year for the past [bold cyan]5 years[/bold cyan]. Company is paying dividends for the past {len(divs)} years.\n")

    if years is not None:
        show_growth(last_div, yearly_growth, amount, years)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Year", justify="center")
    table.add_column("Net Income", justify="center")
    table.add_column("Dividends Paid", justify="center")
    table.add_column("Payout Ratio", justify="center")

    for pr in ticker.get_payout_ratio_yearly(symbol):
        net_income = pr["net_income"]
        dividends_paid = pr["dividends_paid"]
        payout_ratio = round(pr["payout_ratio"] * 100, 2)
        table.add_row(
            str(pr["year"]), 
            f"£{net_income:,}", 
            f"£{dividends_paid:,}", 
            f"[green]{payout_ratio}%[green]" if net_income > dividends_paid else f"[red]{payout_ratio}%[red]"
        )

    console.print(table)
