"""
Static domain reference data.

Kept separate from services/ on purpose: this is *data*, not *logic*.
If this grew large or needed to be edited without a redeploy, it would move
to a database table — noted as a natural next step in the README.
"""

# item name (lowercase) -> category
CATEGORY_MAP: dict[str, str] = {
    "milk": "Dairy", "cheese": "Dairy", "yogurt": "Dairy", "butter": "Dairy",
    "cream": "Dairy", "paneer": "Dairy",
    "apple": "Produce", "apples": "Produce", "banana": "Produce", "bananas": "Produce",
    "orange": "Produce", "oranges": "Produce", "tomato": "Produce", "tomatoes": "Produce",
    "onion": "Produce", "onions": "Produce", "potato": "Produce", "potatoes": "Produce",
    "spinach": "Produce", "carrot": "Produce", "carrots": "Produce",
    "bread": "Bakery", "bun": "Bakery", "buns": "Bakery", "bagel": "Bakery",
    "chips": "Snacks", "cookies": "Snacks", "biscuits": "Snacks", "chocolate": "Snacks",
    "water": "Beverages", "juice": "Beverages", "soda": "Beverages", "coffee": "Beverages",
    "tea": "Beverages",
    "chicken": "Meat & Seafood", "fish": "Meat & Seafood", "eggs": "Meat & Seafood",
    "rice": "Pantry", "sugar": "Pantry", "salt": "Pantry", "flour": "Pantry",
    "oil": "Pantry", "pasta": "Pantry",
    "toothpaste": "Personal Care", "soap": "Personal Care", "shampoo": "Personal Care",
}

DEFAULT_CATEGORY = "Other"

# item -> ordered list of substitute suggestions
SUBSTITUTES: dict[str, list[str]] = {
    "milk": ["almond milk", "oat milk", "soy milk"],
    "sugar": ["honey", "stevia", "jaggery"],
    "butter": ["margarine", "olive oil"],
    "bread": ["multigrain bread", "gluten-free bread"],
    "rice": ["quinoa", "cauliflower rice"],
    "chips": ["baked chips", "roasted makhana"],
}

# month (1-12) -> in-season items, for seasonal recommendations
SEASONAL_ITEMS: dict[int, list[str]] = {
    1: ["oranges", "carrots", "spinach"], 2: ["oranges", "carrots", "spinach"],
    3: ["strawberries", "peas", "spinach"], 4: ["strawberries", "mangoes"],
    5: ["mangoes", "watermelon"], 6: ["mangoes", "watermelon", "cucumber"],
    7: ["watermelon", "cucumber", "corn"], 8: ["corn", "peaches", "berries"],
    9: ["apples", "pumpkin", "grapes"], 10: ["apples", "pumpkin", "sweet potato"],
    11: ["pumpkin", "sweet potato", "cranberries"], 12: ["oranges", "pomegranate"],
}
