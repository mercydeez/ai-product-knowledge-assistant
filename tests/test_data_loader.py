"""Basic tests for project foundation."""

import unittest

from src.config import DATA_PATH
from src.utils.data_loader import load_json


class TestDataLoader(unittest.TestCase):
    def test_products_can_be_loaded(self) -> None:
        products = load_json(DATA_PATH)

        self.assertGreaterEqual(len(products), 10)
        self.assertIsInstance(products[0], dict)
        self.assertIn("id", products[0])
        self.assertIn("name", products[0])


if __name__ == "__main__":
    unittest.main()
