"""
Core data models for Alakh Da Dhaaba
"""

import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional, List, Dict
from config import POINTS_PER_RUPEE

class User:
    """Represents a user account"""
    
    def __init__(self, username: str, name: str, password: str, wallet: int = 500):
        self.username = username.lower()
        self.name = name
        self.password_hash = self._hash_password(password)
        self.wallet = wallet
        self.food_points = 0
        self.favorites: List[Dict] = []
        self.reservations: List[str] = []
        self.orders: List[str] = []
        self.reviews: List[Dict] = []
        self.created_at = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password with a unique salt and PBKDF2-HMAC-SHA256"""
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"
    
    def verify_password(self, password: str) -> bool:
        """Check a password, including legacy hashes that can be migrated"""
        if self.password_hash.startswith("pbkdf2_sha256$"):
            try:
                _, iterations, salt_hex, digest_hex = self.password_hash.split("$", 3)
                expected = hashlib.pbkdf2_hmac(
                    "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
                )
                return hmac.compare_digest(expected.hex(), digest_hex)
            except (ValueError, TypeError):
                return False

        legacy_digest = hashlib.sha256(password.encode()).hexdigest()
        if hmac.compare_digest(legacy_digest, self.password_hash):
            self.password_hash = self._hash_password(password)
            return True
        return False
    
    def add_money(self, amount: int) -> None:
        """Add money to wallet"""
        if amount > 0:
            self.wallet += amount
    
    def deduct_money(self, amount: int) -> bool:
        """Deduct money from wallet"""
        if amount >= 0 and amount <= self.wallet:
            self.wallet -= amount
            return True
        return False
    
    def add_points(self, amount_spent: int) -> int:
        """Add food points based on spending"""
        points = amount_spent // POINTS_PER_RUPEE
        self.food_points += points
        return points
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            "password": self.password_hash,
            "name": self.name,
            "wallet": self.wallet,
            "food_points": self.food_points,
            "favorites": self.favorites,
            "reservations": self.reservations,
            "orders": self.orders,
            "reviews": self.reviews,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, username: str, data: Dict) -> 'User':
        """Create User object from dictionary"""
        user = cls.__new__(cls)
        user.username = username
        user.name = data.get("name", username)
        user.password_hash = data.get("password", "")
        user.wallet = data.get("wallet", 0)
        user.food_points = data.get("food_points", 0)
        user.favorites = data.get("favorites", [])
        user.reservations = data.get("reservations", [])
        user.orders = data.get("orders", [])
        user.reviews = data.get("reviews", [])
        user.created_at = data.get("created_at", "")
        return user

class FoodItem:
    """Represents a menu item"""
    
    def __init__(self, name: str, price: int, category: str = "General", 
                 description: str = "", stock: int = 10, rating: float = 4.0):
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.stock = stock
        self.rating = rating
    
    @property
    def is_available(self) -> bool:
        return self.stock > 0
    
    @property
    def sold_out(self) -> bool:
        return not self.is_available
    
    def decrease_stock(self, quantity: int = 1) -> None:
        self.stock = max(0, self.stock - quantity)
    
    def increase_stock(self, quantity: int = 1) -> None:
        self.stock += quantity
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "stock": self.stock,
            "rating": self.rating,
            "sold_out": self.sold_out
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FoodItem':
        return cls(
            name=data.get("name", "Unknown Item"),
            price=data.get("price", 0),
            category=data.get("category", "General"),
            description=data.get("description", ""),
            stock=data.get("stock", 10),
            rating=data.get("rating", 4.0)
        )

class Restaurant:
    """Represents a restaurant"""
    
    def __init__(self, name: str, emoji: str = "🍽️", total_seats: int = 20):
        self.name = name
        self.emoji = emoji
        self.total_seats = total_seats
        self.available_seats = total_seats
        self.menu: Dict[str, FoodItem] = {}
    
    def add_item(self, item: FoodItem) -> str:
        item_number = str(len(self.menu) + 1)
        self.menu[item_number] = item
        return item_number
    
    def get_item(self, item_number: str) -> Optional[FoodItem]:
        return self.menu.get(item_number)
    
    def book_seats(self, count: int) -> bool:
        if count <= self.available_seats:
            self.available_seats -= count
            return True
        return False
    
    def release_seats(self, count: int) -> None:
        self.available_seats = min(self.total_seats, self.available_seats + count)
    
    def reset_seats(self) -> None:
        self.available_seats = self.total_seats
    
    def to_dict(self) -> Dict:
        return {
            "emoji": self.emoji,
            "total_seats": self.total_seats,
            "available_seats": self.available_seats,
            "menu": {num: item.to_dict() for num, item in self.menu.items()}
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict) -> 'Restaurant':
        restaurant = cls(
            name=name,
            emoji=data.get("emoji", "🍽️"),
            total_seats=data.get("total_seats", 20)
        )
        restaurant.available_seats = data.get("available_seats", restaurant.total_seats)
        for num, item_data in data.get("menu", {}).items():
            restaurant.menu[num] = FoodItem.from_dict(item_data)
        return restaurant

class CartItem:
    """Represents an item in the cart"""
    
    def __init__(self, name: str, price: int, quantity: int, restaurant: str, item_number: str = "", max_quantity: int = 0):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.restaurant = restaurant
        self.item_number = item_number
        self.max_quantity = max_quantity
    
    @property
    def total(self) -> int:
        return self.price * self.quantity
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "restaurant": self.restaurant,
            "item_number": self.item_number,
        }

class Cart:
    """Represents a shopping cart"""
    
    def __init__(self):
        self.items: List[CartItem] = []
    
    def add_item(self, item: FoodItem, restaurant_name: str, quantity: int = 1, item_number: str = "") -> bool:
        if quantity <= 0:
            return False
        for cart_item in self.items:
            if cart_item.item_number == item_number and cart_item.restaurant == restaurant_name:
                if cart_item.quantity + quantity <= item.stock:
                    cart_item.quantity += quantity
                    return True
                return False
        
        if quantity <= item.stock:
            self.items.append(CartItem(item.name, item.price, quantity, restaurant_name, item_number, item.stock))
            return True
        return False
    
    def remove_item(self, index: int) -> bool:
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False
    
    def update_quantity(self, index: int, new_quantity: int) -> bool:
        if 0 <= index < len(self.items):
            if new_quantity <= 0:
                return self.remove_item(index)
            if self.items[index].max_quantity and new_quantity > self.items[index].max_quantity:
                return False
            self.items[index].quantity = new_quantity
            return True
        return False
    
    def clear(self) -> None:
        self.items = []
    
    @property
    def total(self) -> int:
        return sum(item.total for item in self.items)
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
    
    def to_list(self) -> List[Dict]:
        return [item.to_dict() for item in self.items]

class Order:
    """Represents an order"""
    
    STATUS_FLOW = {
        "Preparing": ["Confirmed", "Cancelled"],
        "Confirmed": ["Ready", "Cancelled"],
        "Ready": ["Delivered", "Cancelled"],
        "Delivered": [],
        "Cancelled": []
    }
    
    def __init__(self, order_id: str, username: str, items: List[Dict], total: int):
        self.id = order_id
        self.username = username
        self.items = items
        self.total = total
        self.status = "Preparing"
        self.date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    
    def update_status(self, new_status: str) -> bool:
        if new_status in self.STATUS_FLOW.get(self.status, []):
            self.status = new_status
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "date": self.date
        }

class Reservation:
    """Represents a seat reservation"""
    
    def __init__(self, reservation_id: str, username: str, restaurant: str, seats: int):
        self.id = reservation_id
        self.username = username
        self.restaurant = restaurant
        self.seats = seats
        self.date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        self.status = "Confirmed"
    
    def cancel(self) -> None:
        self.status = "Cancelled"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "restaurant": self.restaurant,
            "seats": self.seats,
            "date": self.date,
            "status": self.status
        }

class Review:
    """Represents a review"""
    
    def __init__(self, username: str, restaurant: str, rating: int, comment: str):
        self.username = username
        self.restaurant = restaurant
        self.rating = rating
        self.comment = comment
        self.date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "restaurant": self.restaurant,
            "rating": self.rating,
            "comment": self.comment,
            "date": self.date
        }

class Coupon:
    """Represents a discount coupon"""
    
    def __init__(self, code: str, coupon_type: str, value: int, description: str = ""):
        self.code = code.upper()
        self.type = coupon_type.lower()
        self.value = value
        self.description = description
    
    def apply(self, total: int) -> tuple:
        if total < 0:
            return 0, 0
        if self.type == "percent":
            discount = (total * self.value) // 100
        else:
            discount = self.value
        
        discount = max(0, min(discount, total))
        return total - discount, discount
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "type": self.type,
            "value": self.value,
            "description": self.description
        }