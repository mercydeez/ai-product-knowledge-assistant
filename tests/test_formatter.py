"""Tests for the product-to-document formatting in src/preprocessing/formatter.py."""

import unittest

from src.preprocessing.formatter import format_product_as_document, format_products_as_documents


def _make_product(**overrides) -> dict:
    product = {
        "id": "SKU-1001",
        "name": "Luna Everyday Cotton Shirt",
        "category": "Tops",
        "brand": "Luna",
        "color": "White",
        "material": "100% Cotton",
        "price": 1499,
        "sizes": ["S", "M", "L"],
        "stock": 25,
        "description": "A breathable everyday cotton shirt.",
        "care_instructions": "Machine wash cold.",
    }
    product.update(overrides)
    return product


class TestFormatProductAsDocument(unittest.TestCase):
    def test_all_fields_appear_in_the_formatted_text(self) -> None:
        document = format_product_as_document(_make_product())

        text = document["text"]
        self.assertIn("Product ID: SKU-1001", text)
        self.assertIn("Product Name: Luna Everyday Cotton Shirt", text)
        self.assertIn("Category: Tops", text)
        self.assertIn("Brand: Luna", text)
        self.assertIn("Color: White", text)
        self.assertIn("Material: 100% Cotton", text)
        self.assertIn("Price: INR 1499", text)
        self.assertIn("Available Sizes: S, M, L", text)
        self.assertIn("Stock: 25", text)
        self.assertIn("Description: A breathable everyday cotton shirt.", text)
        self.assertIn("Care Instructions: Machine wash cold.", text)

    def test_fields_appear_in_a_stable_order(self) -> None:
        document = format_product_as_document(_make_product())

        lines = document["text"].splitlines()
        prefixes = [line.split(":", 1)[0] for line in lines]
        self.assertEqual(
            prefixes,
            [
                "Product ID",
                "Product Name",
                "Category",
                "Brand",
                "Color",
                "Material",
                "Price",
                "Available Sizes",
                "Stock",
                "Description",
                "Care Instructions",
            ],
        )

    def test_missing_sizes_defaults_to_an_empty_list(self) -> None:
        product = _make_product()
        del product["sizes"]

        document = format_product_as_document(product)

        self.assertIn("Available Sizes: ", document["text"])

    def test_returned_dict_carries_product_id_and_name(self) -> None:
        document = format_product_as_document(_make_product(id="SKU-2002", name="Test Jeans"))

        self.assertEqual(document["product_id"], "SKU-2002")
        self.assertEqual(document["product_name"], "Test Jeans")


class TestFormatProductsAsDocuments(unittest.TestCase):
    def test_formats_every_product_in_the_list(self) -> None:
        products = [_make_product(id="SKU-1"), _make_product(id="SKU-2")]

        documents = format_products_as_documents(products)

        self.assertEqual([doc["product_id"] for doc in documents], ["SKU-1", "SKU-2"])

    def test_empty_list_produces_no_documents(self) -> None:
        self.assertEqual(format_products_as_documents([]), [])


if __name__ == "__main__":
    unittest.main()
