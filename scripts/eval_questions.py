"""Shared hand-built question set used by both eval scripts.

Each question is phrased to clearly match exactly one product's formatted
document (see src/preprocessing/formatter.py), mirroring data/products.json.
"""


def _case(question: str, expected_product_id: str) -> dict:
    return {"question": question, "expected_product_id": expected_product_id}


EVAL_QUESTIONS = [
    _case("I need a breathable white cotton shirt for everyday wear.", "SKU-1001"),
    _case("Looking for black slim-fit stretch denim jeans for smart casual wear.", "SKU-1002"),
    _case("Show me a lightweight floral midi dress for warm weather.", "SKU-1003"),
    _case("I want a lightweight linen overshirt for layering.", "SKU-1004"),
    _case("Recommend a moisture-wicking navy polo for travel or active days.", "SKU-1005"),
    _case("I need tailored olive straight-leg trousers for the office.", "SKU-1006"),
    _case("Looking for a soft lavender knit cardigan for transitional weather.", "SKU-1007"),
    _case("Show me charcoal cargo joggers with utility pockets.", "SKU-1008"),
    _case("I want an elegant emerald satin blouse for a dressy occasion.", "SKU-1009"),
    _case("Recommend a water-resistant forest green hooded jacket for hiking.", "SKU-1010"),
    _case("I need a relaxed-fit heather grey graphic t-shirt for weekends.", "SKU-1011"),
    _case("Show me a flowing dusty rose pleated midi skirt.", "SKU-1012"),
    _case("I want a relaxed chambray shirt with roll-up sleeves for the weekend.", "SKU-1013"),
    _case("Show me a ribbed tank top for layering in warm weather.", "SKU-1014"),
    _case("I need flowing wide-leg palazzo pants with a high-rise waist.", "SKU-1015"),
    _case("Looking for tailored chino shorts with a bit of stretch.", "SKU-1016"),
    _case("Recommend a mustard wrap dress with three-quarter sleeves.", "SKU-1017"),
    _case("Show me a sleeveless shift dress for easy day-to-evening wear.", "SKU-1018"),
    _case("I want a lightweight quilted puffer vest for extra warmth.", "SKU-1019"),
    _case("Looking for a classic washed denim jacket with chest pockets.", "SKU-1020"),
    _case("I need a fitted sage turtleneck pullover to layer under jackets.", "SKU-1021"),
    _case("Show me an oversized chunky knit sweater for cold weather.", "SKU-1022"),
    _case("Recommend a mustard A-line denim skirt with a button-front placket.", "SKU-1023"),
    _case("I want a flirty pleated mini skirt with a chiffon overlay.", "SKU-1024"),
]
