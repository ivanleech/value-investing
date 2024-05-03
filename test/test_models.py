import unittest
from context import models
from models import Model


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()
        print("hi")

    def test_get_current_price(self):
        ticker = "AAPL"
        current_price = self.model.get_current_price(ticker)
        self.assertIsInstance(current_price, float)
