from __future__ import annotations
from typing import Tuple
from dataclasses import dataclass, field
from currency_converter import CurrencyConverter

GBP = "GBP"
GBp = "GBp"
USD = "USD"
EUR = "EUR"

VALID_CURRENCY = [GBP, GBp, USD, EUR]

@dataclass
class Money:

    amount: float

    currency: str = field(default = GBP)

    def __init__(self, amount: float, currency: str = GBP)-> None:
        self._validate_currency(currency)

        self.cc = CurrencyConverter()
        if currency[-1] == currency[-1].lower():
            amount = amount / 100
            currency = currency.upper()
        self.amount = amount
        self.currency = currency

    def _validate_currency(self, currency: str)-> None:
        assert currency in VALID_CURRENCY, f"Currency {currency} is not in the valid list"

    def get_in_currency(self, currency: str = GBP)-> float:
        self._validate_currency(currency)

        if currency != self.currency:
            return self.cc.convert(self.amount, self.currency, currency)

        return self.amount

    def get_amount(self)-> Tuple[float, str]:
        return (self.amount, self.currency,)

    def to_dict(self)-> dict:
        return {
            "currency": GBP,
            "amount": self.get_in_currency(GBP)
        }

    def __add__(self, money: Money)-> Money:
        return self.amount + money.get_in_currency(self.currency)

    def __sub__(self, money: Money)-> Money:
        return self.amount - money.get_in_currency(self.currency)

    def __mul__(self, money: Money)-> Money:
        return self.amount * money.get_in_currency(self.currency)

    def __truediv__(self, money: Money)-> Money:
        return self.amount / money.get_in_currency(self.currency)

    def __eq__(self, money: Money)-> bool:
        return self.amount == money.get_in_currency(self.currency)

    def __lt__(self, money: Money)-> bool:
        return self.amount < money.get_in_currency(self.currency)

    def __le__(self, money: Money)-> bool:
        return self.amount <= money.get_in_currency(self.currency)

    def __gt__(self, money: Money)-> bool:
        return self.amount > money.get_in_currency(self.currency)

    def __ge__(self, money: Money)-> bool:
        return self.amount >= money.get_in_currency(self.currency)

if __name__ == "__main__":
    a = Money(245, "GBP")
    b = Money(200, "USD")

    a += b
    print(a)



