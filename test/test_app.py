import unittest
from context import app


class TestApp(unittest.TestCase):

    def setUp(self):
        print("setup")

    def test_index(self):
        print("should fail")
        self.assertTrue(True)
