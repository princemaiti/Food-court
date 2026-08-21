"""
Database management for Alakh Da Dhaaba
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict
from config import BACKUP_DIR, DATA_FILE, MAX_LOG_ENTRIES
from ui import warn

class Database:
    """Handles all data persistence"""
    
    def __init__(self):
        self.data = self.load()
    
    def load(self) -> Dict:
        """Load data from file"""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        if not os.path.exists(DATA_FILE):
            return self._create_default_data()
        
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if self._enrich_catalog(data):
                self.data = data
                self.save()
            return data
        except (json.JSONDecodeError, OSError):
            self._preserve_corrupt_data()
            warn("Data file corrupted. A copy was preserved in backups; creating fresh database.")
            return self._create_default_data()

    def _preserve_corrupt_data(self) -> None:
        """Keep an unreadable data file before creating replacement data."""
        if not os.path.exists(DATA_FILE):
            return
        os.makedirs(BACKUP_DIR, exist_ok=True)
        filename = f"corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            shutil.copy2(DATA_FILE, os.path.join(BACKUP_DIR, filename))
        except OSError:
            pass
    
    def save(self) -> None:
        """Save data to file"""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_user(self, username: str) -> Dict:
        """Return one user record without requiring callers to know storage details."""
        return self.data.get("users", {}).get(username, {})

    def get_order(self, order_id: str) -> Dict:
        """Return one order by its stable identifier."""
        return next((order for order in self.data.get("orders", []) if order.get("id") == order_id), {})

    def get_restaurant(self, name: str) -> Dict:
        """Return one restaurant record by its legacy display name."""
        return self.data.get("restaurants", {}).get(name, {})

    def get_orders_by_user(self, username: str) -> list:
        """Return orders belonging to one user."""
        return [order for order in self.data.get("orders", []) if order.get("username") == username]
    
    def _create_default_data(self) -> Dict:
        """Create default data structure"""
        data = {
            "users": {},
            "restaurants": self._get_default_restaurants(),
            "orders": [],
            "reservations": [],
            "reviews": [],
            "coupons": [
                {"code": "SAVE10", "type": "percent", "value": 10, "description": "10% off order"},
                {"code": "FLAT50", "type": "flat", "value": 50, "description": "₹50 off order"},
                {"code": "WELCOME20", "type": "percent", "value": 20, "description": "20% off your first order"},
                {"code": "FEAST100", "type": "flat", "value": 100, "description": "₹100 off orders above ₹700"},
                {"code": "WEEKEND15", "type": "percent", "value": 15, "description": "15% weekend food festival offer"}
            ],
            "announcements": [
                "🎉 Welcome to Alakh Da Dhaaba!",
                "🔥 Get delicious food from our best restaurants."
            ],
            "activity_logs": [],
            "next_order_id": 1001,
            "next_reservation_id": 501
        }
        
        # Add default users
        from models import User
        prince = User("prince", "Prince", "2007", 1000)
        winkle = User("winkle", "Winkle", "2711", 1000)
        data["users"]["prince"] = prince.to_dict()
        data["users"]["winkle"] = winkle.to_dict()
        
        self.data = data
        self.save()
        return data
    
    def _get_default_restaurants(self) -> Dict:
        """Get default restaurant data"""
        restaurants = {
            "Pizza Palace": {
                "emoji": "🍕",
                "total_seats": 20,
                "available_seats": 20,
                "menu": {
                    "1": {"name": "Margherita Pizza", "price": 149, "category": "Fast Food", "description": "Freshly baked with rich cheese", "stock": 25, "rating": 4.5},
                    "2": {"name": "Farmhouse Pizza", "price": 199, "category": "Fast Food", "description": "Loaded with fresh vegetables", "stock": 25, "rating": 4.3},
                    "3": {"name": "Paneer Tikka Pizza", "price": 229, "category": "Fast Food", "description": "Spicy paneer with mint chutney", "stock": 20, "rating": 4.6},
                    "4": {"name": "Cheese Burst Pizza", "price": 249, "category": "Fast Food", "description": "Extra cheese in every bite", "stock": 20, "rating": 4.7},
                    "5": {"name": "Garlic Bread", "price": 119, "category": "Fast Food", "description": "Buttery garlic goodness", "stock": 30, "rating": 4.2},
                    "6": {"name": "French Fries", "price": 89, "category": "Fast Food", "description": "Crispy golden fries", "stock": 40, "rating": 4.0},
                    "7": {"name": "Cold Coffee", "price": 99, "category": "Beverages", "description": "Chilled coffee delight", "stock": 35, "rating": 4.1},
                    "8": {"name": "Chocolate Shake", "price": 129, "category": "Beverages", "description": "Thick chocolate shake", "stock": 30, "rating": 4.4},
                    "9": {"name": "Brownie with Ice Cream", "price": 149, "category": "Desserts", "description": "Warm brownie with vanilla ice cream", "stock": 15, "rating": 4.8},
                    "10": {"name": "Veggie Supreme Pizza", "price": 219, "category": "Fast Food", "description": "All veggies on one pizza", "stock": 25, "rating": 4.2}
                }
            },
            "Wok Express": {
                "emoji": "🍜",
                "total_seats": 15,
                "available_seats": 15,
                "menu": {
                    "1": {"name": "Veg Hakka Noodles", "price": 129, "category": "Chinese", "description": "Wok-tossed noodles", "stock": 30, "rating": 4.3},
                    "2": {"name": "Schezwan Fried Rice", "price": 139, "category": "Chinese", "description": "Spicy schezwan rice", "stock": 30, "rating": 4.4},
                    "3": {"name": "Chilli Paneer", "price": 169, "category": "Chinese", "description": "Spicy paneer with peppers", "stock": 25, "rating": 4.5},
                    "4": {"name": "Veg Fried Rice", "price": 119, "category": "Chinese", "description": "Classic fried rice", "stock": 30, "rating": 4.0},
                    "5": {"name": "Veg Momos", "price": 99, "category": "Chinese", "description": "Steamed vegetable dumplings", "stock": 35, "rating": 4.6},
                    "6": {"name": "Spring Rolls", "price": 109, "category": "Chinese", "description": "Crispy vegetable rolls", "stock": 25, "rating": 4.1},
                    "7": {"name": "Manchurian", "price": 139, "category": "Chinese", "description": "Veg balls in tangy sauce", "stock": 25, "rating": 4.2},
                    "8": {"name": "Hot & Sour Soup", "price": 89, "category": "Chinese", "description": "Spicy and tangy soup", "stock": 20, "rating": 3.9},
                    "9": {"name": "Honey Chilli Potato", "price": 149, "category": "Chinese", "description": "Sweet and spicy potatoes", "stock": 25, "rating": 4.3},
                    "10": {"name": "Fried Momos", "price": 119, "category": "Chinese", "description": "Crispy fried dumplings", "stock": 30, "rating": 4.4}
                }
            },
            "Spice Hub": {
                "emoji": "🍚",
                "total_seats": 25,
                "available_seats": 25,
                "menu": {
                    "1": {"name": "Paneer Butter Masala", "price": 179, "category": "Indian", "description": "Rich creamy paneer curry", "stock": 25, "rating": 4.7},
                    "2": {"name": "Veg Biryani", "price": 159, "category": "Indian", "description": "Fragrant rice with vegetables", "stock": 30, "rating": 4.5},
                    "3": {"name": "Masala Dosa", "price": 99, "category": "Indian", "description": "Crispy dosa with potato filling", "stock": 30, "rating": 4.4},
                    "4": {"name": "Dal Makhani", "price": 139, "category": "Indian", "description": "Creamy black lentils", "stock": 25, "rating": 4.3},
                    "5": {"name": "Butter Naan", "price": 49, "category": "Indian", "description": "Soft buttery bread", "stock": 40, "rating": 4.2},
                    "6": {"name": "Veg Thali", "price": 199, "category": "Indian", "description": "Complete meal with variety", "stock": 20, "rating": 4.5},
                    "7": {"name": "Shahi Paneer", "price": 189, "category": "Indian", "description": "Royal paneer preparation", "stock": 25, "rating": 4.6},
                    "8": {"name": "Jeera Rice", "price": 99, "category": "Indian", "description": "Cumin flavored rice", "stock": 30, "rating": 4.0},
                    "9": {"name": "Gulab Jamun", "price": 69, "category": "Desserts", "description": "Sweet milk solids in syrup", "stock": 35, "rating": 4.8},
                    "10": {"name": "Samosa", "price": 25, "category": "Indian", "description": "Crispy pastry with spiced filling", "stock": 50, "rating": 4.1}
                }
            },
            "Burger Point": {
                "emoji": "🍔",
                "total_seats": 10,
                "available_seats": 10,
                "menu": {
                    "1": {"name": "Classic Veg Burger", "price": 99, "category": "Fast Food", "description": "Crispy veg patty burger", "stock": 30, "rating": 4.2},
                    "2": {"name": "Paneer Crunch Burger", "price": 139, "category": "Fast Food", "description": "Paneer patty with crunch", "stock": 25, "rating": 4.4},
                    "3": {"name": "Double Cheese Burger", "price": 159, "category": "Fast Food", "description": "Extra cheese loaded burger", "stock": 25, "rating": 4.6},
                    "4": {"name": "Aloo Tikki Burger", "price": 79, "category": "Fast Food", "description": "Classic Indian style burger", "stock": 30, "rating": 4.0},
                    "5": {"name": "Peri Peri Fries", "price": 109, "category": "Fast Food", "description": "Spicy peri peri fries", "stock": 35, "rating": 4.3},
                    "6": {"name": "Cheese Nachos", "price": 129, "category": "Fast Food", "description": "Crispy nachos with cheese", "stock": 25, "rating": 4.1},
                    "7": {"name": "Oreo Shake", "price": 139, "category": "Beverages", "description": "Cookies and cream shake", "stock": 30, "rating": 4.5},
                    "8": {"name": "Veg Nuggets", "price": 109, "category": "Fast Food", "description": "Crispy vegetable nuggets", "stock": 30, "rating": 4.0},
                    "9": {"name": "Cheese Balls", "price": 119, "category": "Fast Food", "description": "Melty cheese balls", "stock": 25, "rating": 4.3},
                    "10": {"name": "Onion Rings", "price": 99, "category": "Fast Food", "description": "Crispy battered onion rings", "stock": 25, "rating": 3.9}
                }
            }
        }
        self._enrich_catalog({"restaurants": restaurants})
        return restaurants

    def _enrich_catalog(self, data: Dict) -> bool:
        """Expand each branch with a varied menu while preserving existing records."""
        restaurants = data.setdefault("restaurants", {})
        new_branches = {
            "Tandoor Terrace": ("🔥", 35, "North Indian", "Live-fire tandoor favourites and smoky grills.", "12:00 PM - 11:30 PM", "Dine-in / Takeaway"),
            "Dosa Junction": ("🥞", 28, "South Indian", "Crisp dosas, comforting idlis and filter coffee.", "8:00 AM - 10:30 PM", "Quick service"),
            "Sweet Truth": ("🍨", 22, "Desserts & Cafe", "A relaxed dessert cafe for sweet celebrations.", "11:00 AM - 12:00 AM", "Cafe / Takeaway"),
        }
        changed = False
        for name, (emoji, seats, cuisine, description, opening_hours, service_style) in new_branches.items():
            if name not in restaurants:
                restaurants[name] = {
                    "emoji": emoji,
                    "total_seats": seats,
                    "available_seats": seats,
                    "cuisine": cuisine,
                    "description": description,
                    "opening_hours": opening_hours,
                    "service_style": service_style,
                    "menu": {},
                }
                changed = True

        menu_sets = {
            "Pizza Palace": [
                ("Tandoori Paneer Pizza", 239, "Fast Food", "Smoky paneer, onion and capsicum"),
                ("Corn & Cheese Pizza", 189, "Fast Food", "Sweet corn with a creamy cheese blend"),
                ("Pesto Veg Pizza", 259, "Fast Food", "Basil pesto with roasted vegetables"),
                ("Jalapeno Popper Pizza", 249, "Fast Food", "Creamy cheese and fiery jalapenos"),
                ("Cheesy Pasta Bake", 179, "Pasta", "Oven baked pasta in rich tomato sauce"),
                ("Arrabbiata Pasta", 159, "Pasta", "Spicy tomato pasta with herbs"),
                ("Loaded Potato Wedges", 139, "Sides", "Crispy wedges with cheese dip"),
                ("Lemon Iced Tea", 79, "Beverages", "Bright and refreshing house iced tea"),
                ("Mango Smoothie", 119, "Beverages", "Thick seasonal mango smoothie"),
                ("Tiramisu Cup", 159, "Desserts", "Coffee soaked cream and cocoa layers"),
            ],
            "Wok Express": [
                ("Burnt Garlic Noodles", 149, "Chinese", "Noodles tossed with crisp garlic"),
                ("Schezwan Noodles", 159, "Chinese", "Hot wok noodles with schezwan sauce"),
                ("Kung Pao Paneer", 189, "Chinese", "Paneer, peanuts and peppers in wok sauce"),
                ("Crispy Corn", 129, "Chinese", "Crunchy corn with chilli and spring onion"),
                ("Veg Manchow Soup", 109, "Soups", "Spicy soup topped with fried noodles"),
                ("Sweet Corn Soup", 99, "Soups", "Comforting soup with sweet corn"),
                ("Thai Green Curry", 219, "Thai", "Fragrant coconut curry with vegetables"),
                ("Pad Thai Noodles", 199, "Thai", "Tamarind noodles with peanuts"),
                ("Chilli Garlic Rice", 149, "Chinese", "Aromatic rice with garlic and chilli"),
                ("Mango Bubble Tea", 139, "Beverages", "Chilled mango tea with chewy pearls"),
            ],
            "Spice Hub": [
                ("Chole Bhature", 149, "Indian", "Spiced chickpeas with fluffy bhature"),
                ("Rajma Chawal", 139, "Indian", "Slow cooked kidney beans with rice"),
                ("Kadhai Paneer", 199, "Indian", "Paneer with peppers in aromatic masala"),
                ("Malai Kofta", 209, "Indian", "Soft kofta in creamy tomato gravy"),
                ("Tandoori Roti", 29, "Indian", "Clay oven baked whole wheat bread"),
                ("Garlic Naan", 69, "Indian", "Tandoor naan topped with garlic"),
                ("Veg Seekh Kebab", 179, "Starters", "Smoky minced vegetable kebabs"),
                ("Hara Bhara Kebab", 159, "Starters", "Spinach and pea kebabs"),
                ("Mango Lassi", 89, "Beverages", "Chilled yoghurt drink with mango"),
                ("Rasmalai", 99, "Desserts", "Soft cheese dumplings in saffron milk"),
            ],
            "Burger Point": [
                ("BBQ Paneer Burger", 169, "Fast Food", "Grilled paneer with smoky BBQ sauce"),
                ("Mushroom Melt Burger", 179, "Fast Food", "Savoury mushrooms and melted cheese"),
                ("Spicy Mexican Burger", 159, "Fast Food", "Jalapeno salsa and crunchy patty"),
                ("Crispy Corn Burger", 129, "Fast Food", "Golden corn patty with fresh lettuce"),
                ("Classic Veg Wrap", 119, "Wraps", "Seasoned vegetables in a soft wrap"),
                ("Paneer Tikka Wrap", 159, "Wraps", "Tandoori paneer with mint dressing"),
                ("Chilli Cheese Toast", 109, "Sides", "Toasted bread with cheese and chilli"),
                ("Masala Lemonade", 69, "Beverages", "Zesty lemonade with Indian spices"),
                ("Strawberry Shake", 139, "Beverages", "Creamy strawberry milkshake"),
                ("Choco Lava Cake", 129, "Desserts", "Warm cake with a molten centre"),
            ],
            "taj hotel": [
                ("Royal Paneer Platter", 349, "Fine Dining", "Chef selection of paneer specialities"),
                ("Awadhi Veg Biryani", 299, "Fine Dining", "Fragrant rice with saffron and vegetables"),
                ("Dal Bukhara", 269, "Fine Dining", "Slow simmered black lentils"),
                ("Mughlai Vegetable Korma", 289, "Fine Dining", "Vegetables in a rich nut gravy"),
                ("Tandoori Mushroom", 229, "Starters", "Charred mushrooms with smoky spices"),
                ("Stuffed Tandoori Aloo", 219, "Starters", "Potatoes filled with spiced cheese"),
                ("Roomali Roti", 49, "Indian", "Thin handkerchief-style bread"),
                ("Saffron Lassi", 119, "Beverages", "Silky yoghurt with saffron"),
                ("Rose Falooda", 159, "Beverages", "Rose milk with basil seeds and ice cream"),
                ("Royal Shahi Tukda", 179, "Desserts", "Bread pudding with rabri and nuts"),
            ],
            "Tandoor Terrace": [
                ("Paneer Tikka", 219, "Tandoor", "Char-grilled paneer with peppers"),
                ("Achari Soya Chaap", 199, "Tandoor", "Tangy pickled spice soya chaap"),
                ("Tandoori Broccoli", 189, "Tandoor", "Charred broccoli with creamy marinade"),
                ("Dahi Ke Kebab", 179, "Starters", "Crisp yoghurt kebabs with herbs"),
                ("Afghani Paneer", 239, "Tandoor", "Mild creamy paneer tikka"),
                ("Tandoori Platter", 399, "Combos", "A generous mix of house tandoor favourites"),
                ("Dal Tadka", 139, "Indian", "Yellow lentils tempered with garlic"),
                ("Jeera Pulao", 119, "Indian", "Basmati rice with toasted cumin"),
                ("Mint Chaas", 69, "Beverages", "Cool spiced buttermilk with mint"),
                ("Kulfi Falooda", 149, "Desserts", "Traditional kulfi with falooda"),
            ],
            "Dosa Junction": [
                ("Mysore Masala Dosa", 139, "South Indian", "Crisp dosa with spicy red chutney"),
                ("Paneer Dosa", 169, "South Indian", "Dosa filled with masala paneer"),
                ("Cheese Corn Dosa", 159, "South Indian", "Fusion dosa with corn and cheese"),
                ("Onion Uttapam", 109, "South Indian", "Thick savoury pancake with onion"),
                ("Podi Idli", 89, "South Indian", "Steamed idlis tossed in gunpowder spice"),
                ("Medu Vada", 99, "South Indian", "Crisp lentil fritters with sambar"),
                ("Mini Idli Sambar", 89, "South Indian", "Soft bite-sized idlis in sambar"),
                ("Filter Coffee", 69, "Beverages", "South Indian coffee brewed traditionally"),
                ("Tender Coconut Cooler", 99, "Beverages", "Refreshing coconut and lime drink"),
                ("Kesari Bath", 79, "Desserts", "Warm semolina sweet with saffron"),
            ],
            "Sweet Truth": [
                ("Belgian Waffle", 179, "Desserts", "Crisp waffle with chocolate drizzle"),
                ("Classic Cheesecake", 199, "Desserts", "Silky baked cheesecake slice"),
                ("Brownie Sundae", 189, "Desserts", "Warm brownie, ice cream and sauce"),
                ("Red Velvet Pastry", 149, "Desserts", "Velvety sponge with cream cheese"),
                ("Gulab Jamun Sundae", 159, "Desserts", "Warm gulab jamun with vanilla ice cream"),
                ("Fruit Cream", 129, "Desserts", "Seasonal fruits folded through cream"),
                ("Oreo Thick Shake", 169, "Beverages", "Rich cookie shake with whipped cream"),
                ("Cold Cocoa", 119, "Beverages", "Chilled cocoa with a smooth finish"),
                ("Classic Hot Chocolate", 129, "Beverages", "Warm chocolate topped with foam"),
                ("Pistachio Ice Cream", 99, "Ice Cream", "Creamy roasted pistachio scoop"),
            ],
        }
        menu_sets.update({
            "taj hotel": [
                ("Nawabi Veg Galouti", 249, "Starters", "Melt-in-the-mouth vegetarian kebab"),
                ("Kashmiri Dum Aloo", 229, "Fine Dining", "Baby potatoes in saffron gravy"),
                ("Paneer Lababdar", 279, "Fine Dining", "Paneer in a silky tomato sauce"),
                ("Subz Handi", 259, "Fine Dining", "Seasonal vegetables in a clay pot"),
                ("Truffle Mushroom Bites", 299, "Starters", "Mushrooms finished with truffle oil"),
                ("Herbed Rice Pilaf", 189, "Sides", "Fragrant rice with garden herbs"),
                ("Cucumber Mint Cooler", 109, "Beverages", "Fresh cucumber, mint and lime"),
                ("Kesar Badam Milk", 139, "Beverages", "Chilled almond milk with saffron"),
                ("Baked Rasgulla", 149, "Desserts", "Soft rasgulla baked with cream"),
                ("Chocolate Hazelnut Tart", 219, "Desserts", "Crisp tart with hazelnut chocolate"),
            ],
            "Tandoor Terrace": [
                ("Tandoori Pineapple", 169, "Tandoor", "Sweet pineapple with smoky spice"),
                ("Bharwan Tandoori Aloo", 189, "Tandoor", "Stuffed potatoes from the clay oven"),
                ("Soya Chaap Tikka", 209, "Tandoor", "Tender chaap with mint marinade"),
                ("Paneer Kali Mirch", 229, "Tandoor", "Peppery cream-marinated paneer"),
                ("Tandoori Momos", 179, "Starters", "Momos finished over charcoal"),
                ("Smoked Corn Chaat", 129, "Starters", "Charred corn with lime and masala"),
                ("Butter Dal", 159, "Indian", "Creamy lentils finished with butter"),
                ("Basket of Tandoori Breads", 139, "Indian", "Assorted fresh breads from the tandoor"),
                ("Aam Panna", 79, "Beverages", "Tart raw mango summer cooler"),
                ("Jalebi with Rabri", 139, "Desserts", "Crisp jalebi with chilled rabri"),
            ],
            "Dosa Junction": [
                ("Ghee Roast Dosa", 149, "South Indian", "Extra crisp dosa roasted in ghee"),
                ("Cheese Masala Dosa", 179, "South Indian", "Masala dosa with melted cheese"),
                ("Ragi Dosa", 119, "South Indian", "Nutritious crisp finger millet dosa"),
                ("Pesarattu", 129, "South Indian", "Green gram crepe with ginger"),
                ("Thatte Idli", 99, "South Indian", "Soft plate-style idli with chutney"),
                ("Kanchipuram Idli", 109, "South Indian", "Pepper and cashew tempered idli"),
                ("Bisi Bele Bath", 139, "South Indian", "Comforting rice and lentil dish"),
                ("Lemon Rice", 99, "South Indian", "Tangy rice with peanuts and curry leaves"),
                ("Rose Milk", 79, "Beverages", "Chilled rose-flavoured milk"),
                ("Mysore Pak", 89, "Desserts", "Traditional gram flour and ghee sweet"),
            ],
            "Sweet Truth": [
                ("Blueberry Cheesecake", 229, "Desserts", "Creamy cheesecake with blueberry topping"),
                ("Lotus Biscoff Cheesecake", 249, "Desserts", "Caramel biscuit cheesecake slice"),
                ("Chocolate Mousse", 159, "Desserts", "Airy dark chocolate mousse"),
                ("Panna Cotta", 179, "Desserts", "Silky vanilla cream with berry sauce"),
                ("Sizzling Brownie", 219, "Desserts", "Hot brownie on a sizzling plate"),
                ("Nutella Crepe", 189, "Desserts", "Thin crepe filled with chocolate hazelnut"),
                ("Mango Frappe", 159, "Beverages", "Blended mango and cream frappe"),
                ("Caramel Macchiato", 149, "Beverages", "Coffee with steamed milk and caramel"),
                ("Cookies and Cream Sundae", 179, "Ice Cream", "Vanilla ice cream with cookie crunch"),
                ("Dry Fruit Kulfi", 129, "Ice Cream", "Traditional kulfi with roasted nuts"),
            ],
        })
        for restaurant_name, items in menu_sets.items():
            restaurant = restaurants.get(restaurant_name)
            if not restaurant:
                continue
            menu = restaurant.setdefault("menu", {})
            for item_name, price, category, description in items:
                if any(item.get("name") == item_name for item in menu.values()):
                    continue
                number = str(max((int(key) for key in menu if str(key).isdigit()), default=0) + 1)
                menu[number] = {
                    "name": item_name,
                    "price": price,
                    "category": category,
                    "description": description,
                    "stock": 18 + (len(menu) % 4) * 7,
                    "rating": round(4.0 + (len(menu) % 10) / 10, 1),
                    "sold_out": False,
                }
                changed = True
        branch_metadata = {
            "Pizza Palace": ("Italian & Fast Food", "Hand-stretched pizzas, baked sides and chilled drinks.", "11:00 AM - 11:30 PM", "Dine-in / Takeaway"),
            "Wok Express": ("Chinese & Thai", "Fast wok cooking with noodles, rice and bright sauces.", "12:00 PM - 11:00 PM", "Quick service"),
            "Spice Hub": ("Indian Vegetarian", "Classic Indian comfort food with family-style portions.", "10:00 AM - 11:00 PM", "Dine-in / Takeaway"),
            "Burger Point": ("Burgers & Snacks", "Casual burgers, wraps, shakes and loaded sides.", "11:00 AM - 12:00 AM", "Quick service"),
            "taj hotel": ("Luxury Indian", "An elevated vegetarian dining experience with royal flavours.", "7:00 AM - 11:30 PM", "Fine dining"),
        }
        for name, (cuisine, description, opening_hours, service_style) in branch_metadata.items():
            restaurant = restaurants.get(name)
            if not restaurant:
                continue
            for key, value in (("cuisine", cuisine), ("description", description), ("opening_hours", opening_hours), ("service_style", service_style)):
                if restaurant.get(key) != value:
                    restaurant[key] = value
                    changed = True
        for restaurant in restaurants.values():
            for item in restaurant.get("menu", {}).values():
                category = item.get("category", "General")
                dietary = "Contains dairy" if any(word in item.get("name", "").lower() for word in ("paneer", "cheese", "cream", "butter", "lassi", "shake", "ice cream", "naan")) else "Vegetarian"
                preparation = 8 + (len(item.get("name", "")) % 6) * 2
                metadata = {"dietary": dietary, "prep_time": preparation, "popular": item.get("rating", 0) >= 4.5}
                for key, value in metadata.items():
                    if item.get(key) != value:
                        item[key] = value
                        changed = True
        if not data.get("demo_data_seeded"):
            self._seed_demo_history(data)
            data["demo_data_seeded"] = True
            changed = True
        if not data.get("customer_history_enhanced"):
            self._enhance_customer_history(data)
            data["customer_history_enhanced"] = True
            changed = True
        changed = self._add_stable_ids(data) or changed
        for coupon in data.setdefault("coupons", []):
            if "used_by" not in coupon:
                coupon["used_by"] = []
                changed = True
        coupon_codes = {coupon.get("code", "").upper() for coupon in data.setdefault("coupons", [])}
        for coupon in [
            {"code": "WELCOME20", "type": "percent", "value": 20, "description": "20% off your first order"},
            {"code": "FEAST100", "type": "flat", "value": 100, "description": "₹100 off orders above ₹700"},
            {"code": "WEEKEND15", "type": "percent", "value": 15, "description": "15% weekend food festival offer"},
        ]:
            if coupon["code"] not in coupon_codes:
                data["coupons"].append(coupon)
                coupon_codes.add(coupon["code"])
                changed = True
        announcements = data.setdefault("announcements", [])
        for announcement in [
            "🍽️ New branches are now serving all-day favourites.",
            "🎁 Use WELCOME20 on your first order at the expanded food court.",
            "🌶️ Chef specials rotate regularly - check every menu for something new.",
        ]:
            if announcement not in announcements:
                announcements.append(announcement)
                changed = True
        for order in data.get("orders", []):
            if order.pop("demo_data", None) is not None:
                changed = True
        return changed

    def _add_stable_ids(self, data: Dict) -> bool:
        """Add durable IDs and relationship fields while preserving old JSON keys."""
        changed = False
        for index, (username, user) in enumerate(data.get("users", {}).items(), 1):
            if "user_id" not in user:
                user["user_id"] = f"user_{index:06d}"
                changed = True
        for index, (name, restaurant) in enumerate(data.get("restaurants", {}).items(), 1):
            if "restaurant_id" not in restaurant:
                restaurant["restaurant_id"] = f"restaurant_{index:06d}"
                changed = True
            for item_index, (item_number, item) in enumerate(restaurant.get("menu", {}).items(), 1):
                if "food_id" not in item:
                    item["food_id"] = f"food_{index:06d}_{item_index:03d}"
                    changed = True
        user_ids = {username: user.get("user_id") for username, user in data.get("users", {}).items()}
        restaurant_ids = {name: restaurant.get("restaurant_id") for name, restaurant in data.get("restaurants", {}).items()}
        for order in data.get("orders", []):
            if "order_id" not in order:
                order["order_id"] = order.get("id")
                changed = True
            if "user_id" not in order:
                order["user_id"] = user_ids.get(order.get("username"))
                changed = True
            for item in order.get("items", []):
                if "restaurant_id" not in item:
                    item["restaurant_id"] = restaurant_ids.get(item.get("restaurant"))
                    changed = True
        for reservation in data.get("reservations", []):
            if "reservation_id" not in reservation:
                reservation["reservation_id"] = reservation.get("id")
                changed = True
            if "user_id" not in reservation:
                reservation["user_id"] = user_ids.get(reservation.get("username"))
                changed = True
            if "restaurant_id" not in reservation:
                reservation["restaurant_id"] = restaurant_ids.get(reservation.get("restaurant"))
                changed = True
        return changed

    def _seed_demo_history(self, data: Dict) -> None:
        """Add realistic demo activity once without touching existing customer history."""
        from models import User

        demo_customers = [
            ("demo_riya", "Riya Sharma", "demo1234", 4200),
            ("demo_arjun", "Arjun Mehta", "demo1234", 6800),
            ("demo_neha", "Neha Kapoor", "demo1234", 3150),
            ("demo_kabir", "Kabir Singh", "demo1234", 9200),
        ]
        for username, name, password, spent in demo_customers:
            if username in data["users"]:
                continue
            user = User(username, name, password, 12000)
            data["users"][username] = user.to_dict()
            order_count = 2
            data["users"][username]["orders"] = []
            paid_total = 0
            for order_number in range(order_count):
                restaurant_names = list(data["restaurants"])
                restaurant_name = restaurant_names[(len(data["orders"]) + order_number) % len(restaurant_names)]
                restaurant = data["restaurants"][restaurant_name]
                menu_items = list(restaurant.get("menu", {}).items())
                item_number, menu_item = menu_items[(len(data["orders"]) + order_number) % len(menu_items)]
                quantity = 3 + (spent // 1000) + order_number
                subtotal = menu_item["price"] * quantity
                coupon_code = "SAVE10" if order_number == 0 else ""
                total = subtotal - (subtotal * 10 // 100) if coupon_code else subtotal
                order_id = f"ALD{data['next_order_id']}"
                data["next_order_id"] += 1
                order = {
                    "id": order_id,
                    "username": username,
                    "items": [{
                        "name": menu_item["name"],
                        "price": menu_item["price"],
                        "quantity": quantity,
                        "restaurant": restaurant_name,
                        "item_number": item_number,
                    }],
                    "subtotal": subtotal,
                    "discount": subtotal - total,
                    "total": total,
                    "coupon_code": coupon_code,
                    "payment_method": "Wallet",
                    "status": "Delivered" if order_number == 0 else "Confirmed",
                    "date": f"{17 + order_number:02d}-08-2026 0{2 + order_number}:15 PM",
                    "demo_data": True,
                }
                data["orders"].append(order)
                data["users"][username]["orders"].append(order_id)
                paid_total += total
                if coupon_code:
                    for coupon in data.get("coupons", []):
                        if coupon.get("code", "").upper() == coupon_code:
                            coupon.setdefault("used_by", []).append(username)
                            break
                data.setdefault("activity_logs", []).append({
                    "time": order["date"],
                    "action": "demo_order_seeded",
                    "username": username,
                    "details": f"Paid {order_id} for ₹{total} using wallet",
                })
            data["users"][username]["wallet"] = 12000 - paid_total
            data["users"][username]["food_points"] = paid_total // 10

    def _enhance_customer_history(self, data: Dict) -> None:
        """Convert seeded accounts into normal customers with complete app activity."""
        rename_map = {
            "demo_riya": "riya_sharma",
            "demo_arjun": "arjun_mehta",
            "demo_neha": "neha_kapoor",
            "demo_kabir": "kabir_singh",
        }
        for old_username, new_username in rename_map.items():
            if old_username in data.get("users", {}) and new_username not in data["users"]:
                data["users"][new_username] = data["users"].pop(old_username)
        for old_username, new_username in rename_map.items():
            for order in data.get("orders", []):
                if order.get("username") == old_username:
                    order["username"] = new_username
            for reservation in data.get("reservations", []):
                if reservation.get("username") == old_username:
                    reservation["username"] = new_username
            for review in data.get("reviews", []):
                if review.get("username") == old_username:
                    review["username"] = new_username
            for log in data.get("activity_logs", []):
                if log.get("username") == old_username:
                    log["username"] = new_username
            for coupon in data.get("coupons", []):
                coupon["used_by"] = [new_username if user == old_username else user for user in coupon.get("used_by", [])]

        customers = ["riya_sharma", "arjun_mehta", "neha_kapoor", "kabir_singh"]
        restaurants = list(data.get("restaurants", {}).items())
        for index, username in enumerate(customers):
            user = data.get("users", {}).get(username)
            if not user or not restaurants:
                continue
            first_restaurant, first_data = restaurants[index % len(restaurants)]
            menu = list(first_data.get("menu", {}).items())
            if not menu:
                continue
            first_number, first_item = menu[index % len(menu)]
            favorite = {
                "name": first_item["name"], "price": first_item["price"],
                "restaurant": first_restaurant, "item_number": first_number,
            }
            if not any(saved.get("item_number") == first_number and saved.get("restaurant") == first_restaurant for saved in user.get("favorites", [])):
                user.setdefault("favorites", []).append(favorite)

            second_restaurant, second_data = restaurants[(index + 2) % len(restaurants)]
            second_menu = list(second_data.get("menu", {}).items())
            second_number, second_item = second_menu[(index + 1) % len(second_menu)]
            second_favorite = {
                "name": second_item["name"], "price": second_item["price"],
                "restaurant": second_restaurant, "item_number": second_number,
            }
            if not any(saved.get("item_number") == second_number and saved.get("restaurant") == second_restaurant for saved in user.get("favorites", [])):
                user.setdefault("favorites", []).append(second_favorite)

            reservation_restaurant, reservation_data = restaurants[(index + 1) % len(restaurants)]
            if not any(item.get("username") == username for item in data.get("reservations", [])):
                seats = 2
                if reservation_data.get("available_seats", 0) >= seats:
                    reservation_data["available_seats"] -= seats
                    reservation_id = f"RES{data['next_reservation_id']}"
                    data["next_reservation_id"] += 1
                    reservation = {
                        "id": reservation_id, "username": username,
                        "restaurant": reservation_restaurant, "seats": seats,
                        "date": f"{22 + index:02d}-08-2026 07:30 PM", "status": "Confirmed",
                    }
                    data.setdefault("reservations", []).append(reservation)
                    user.setdefault("reservations", []).append(reservation_id)

            review = {
                "username": username, "restaurant": first_restaurant,
                "rating": 4 + (index % 2),
                "comment": [
                    "Excellent flavours and quick service.",
                    "Generous portions and a lovely dining experience.",
                    "Fresh food, friendly staff and a clean branch.",
                    "The menu has plenty of great vegetarian choices.",
                ][index],
                "date": f"{21 + index:02d}-08-2026 08:15 PM",
            }
            if not any(item.get("username") == username for item in data.get("reviews", [])):
                data.setdefault("reviews", []).append(review)
                user.setdefault("reviews", []).append(review.copy())

            for action, details in [
                ("user_login", "Customer signed in"),
                ("menu_browsed", f"Browsed {first_restaurant}"),
                ("favorite_added", f"Saved {first_item['name']}"),
                ("reservation_made", f"Reserved seats at {reservation_restaurant}"),
                ("review_added", f"Reviewed {first_restaurant}"),
            ]:
                data.setdefault("activity_logs", []).append({
                    "time": "21-08-2026 08:00 PM", "action": action,
                    "username": username, "details": details,
                })
    
    def backup(self) -> str:
        """Create data backup"""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(BACKUP_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        return path
    
    def restore(self, backup_path: str) -> bool:
        """Restore data from backup"""
        if not os.path.exists(backup_path):
            return False
        with open(backup_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.save()
        return True
    
    def log_activity(self, action: str, username: str = "system", details: str = ""):
        """Log activity"""
        entry = {
            "time": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "action": action,
            "username": username,
            "details": details
        }
        self.data.setdefault("activity_logs", []).append(entry)
        
        if len(self.data["activity_logs"]) > MAX_LOG_ENTRIES:
            self.data["activity_logs"] = self.data["activity_logs"][-MAX_LOG_ENTRIES:]