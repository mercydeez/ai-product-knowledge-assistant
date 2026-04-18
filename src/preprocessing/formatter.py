"""Helpers for converting product records into formatted text documents."""


def format_product_as_document(product: dict) -> dict:
    """Convert a single product dictionary into one clean text document."""
    sizes = ", ".join(product.get("sizes", []))

    lines = [
        f"Product ID: {product['id']}",
        f"Product Name: {product['name']}",
        f"Category: {product['category']}",
        f"Brand: {product['brand']}",
        f"Color: {product['color']}",
        f"Material: {product['material']}",
        f"Price: INR {product['price']}",
        f"Available Sizes: {sizes}",
        f"Stock: {product['stock']}",
        f"Description: {product['description']}",
        f"Care Instructions: {product['care_instructions']}",
    ]

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "text": "\n".join(lines),
    }


def format_products_as_documents(products: list[dict]) -> list[dict]:
    """Convert all product records into formatted text documents."""
    documents = []

    for product in products:
        documents.append(format_product_as_document(product))

    return documents
