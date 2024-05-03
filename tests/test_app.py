import unittest


class TestApp(unittest.TestCase):

    def setUp(self):
        print("setup")

    def test_index(self):
        self.assertTrue(True)
