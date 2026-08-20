"""
Database management for Alakh Da Dhaaba
"""

import json
import os
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
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            warn("Data file corrupted. Creating fresh database.")
            return self._create_default_data()
    
    def save(self) -> None:
        """Save data to file"""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
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
                {"code": "FLAT50", "type": "flat", "value": 50, "description": "₹50 off order"}
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
        return {
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