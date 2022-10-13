import unittest
from src.money import Money, GBP, USD, GBp


class TestMoney(unittest.TestCase):

    def test_default_currency(self):
        m = Money(200)
        (amount, currency) = m.get_amount()

        self.assertEqual(amount, 200)
        self.assertEqual(currency, GBP)

    def test_change_currency(self):
        m = Money(200)
        amount = m.get_in_currency(USD)

        self.assertNotEqual(amount, 200)

    def test_change_penny_to_pounds(self):
        m = Money(200, GBp)
        (amount, currency) = m.get_amount()

        self.assertEqual(amount, 2.0)
        self.assertEqual(currency, GBP)

    def test_operations_with_money(self):
        a = Money(200)
        b = Money(200, USD)

        a_gbp = a.get_in_currency(GBP)
        b_gbp = b.get_in_currency(GBP)

        self.assertEqual(a + b, a_gbp + b_gbp)
        self.assertEqual(a - b, a_gbp - b_gbp)
        self.assertEqual(a * b, a_gbp * b_gbp)
        self.assertEqual(a / b, a_gbp / b_gbp)

    def test_compare_with_money(self):
        a = Money(200)
        b = Money(200, USD)

        a_gbp = a.get_in_currency(GBP)
        b_gbp = b.get_in_currency(GBP)

        self.assertEqual(a == b, a_gbp == b_gbp)
        self.assertEqual(a < b, a_gbp < b_gbp)
        self.assertEqual(a <= b, a_gbp < b_gbp)
        self.assertEqual(a > b, a_gbp > b_gbp)
        self.assertEqual(a >= b, a_gbp > b_gbp)

if __name__ == "__main__":
    unittest.main()