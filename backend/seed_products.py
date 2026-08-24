"""
One-off script to seed the mock product catalog used by voice search.

Run with: python seed_products.py

Test data note (per assignment's "collect test data from public sources"
allowance): prices and product names here are representative mock data
modeled on typical grocery listings, not scraped from a live retailer —
documented explicitly in the README.
"""
from app.core.database import Base, SessionLocal, engine
from app.models.models import Product

Base.metadata.create_all(bind=engine)

PRODUCTS = [
    ("Organic Apples", "Nature's Best", "Produce", 4.99),
    ("Organic Apples", "FreshFarm", "Produce", 5.49),
    ("Bananas", "FreshFarm", "Produce", 1.29),
    ("Whole Milk", "DairyPure", "Dairy", 3.49),
    ("Almond Milk", "SilkGold", "Dairy", 4.29),
    ("Oat Milk", "OatlyBest", "Dairy", 4.79),
    ("Toothpaste", "Colgate", "Personal Care", 3.99),
    ("Toothpaste", "Sensodyne", "Personal Care", 6.49),
    ("Whitening Toothpaste", "Colgate", "Personal Care", 4.99),
    ("White Bread", "WonderLoaf", "Bakery", 2.49),
    ("Multigrain Bread", "NatureBake", "Bakery", 3.29),
    ("Basmati Rice 5kg", "India Gate", "Pantry", 12.99),
    ("Brown Rice 2kg", "India Gate", "Pantry", 6.49),
    ("Potato Chips", "Lays", "Snacks", 2.99),
    ("Baked Chips", "Lays", "Snacks", 3.49),
    ("Orange Juice", "Tropicana", "Beverages", 4.49),
    ("Bottled Water 24pk", "Aquafina", "Beverages", 5.99),
    ("Free Range Eggs (dozen)", "HappyHen", "Meat & Seafood", 3.99),
    ("Chicken Breast 1kg", "FarmFresh", "Meat & Seafood", 8.99),
    ("Cheddar Cheese", "DairyPure", "Dairy", 4.99),
    ("Greek Yogurt", "Chobani", "Dairy", 5.49),
    ("Spinach Bunch", "FreshFarm", "Produce", 2.49),
    ("Tomatoes 1kg", "FreshFarm", "Produce", 2.99),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            print("Products already seeded, skipping.")
            return
        for name, brand, category, price in PRODUCTS:
            db.add(Product(name=name, brand=brand, category=category, price=price))
        db.commit()
        print(f"Seeded {len(PRODUCTS)} products.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
