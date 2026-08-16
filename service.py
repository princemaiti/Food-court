"""
Business logic for Alakh Da Dhaaba
"""

import os
from typing import Optional, List, Dict, Tuple
from models import User, Restaurant, FoodItem, Cart, Order, Reservation, Review, Coupon
from database import Database
from config import RECEIPT_DIR
from ui import success, error, warn, info, money, C

class FoodCourtService:
    """Main business logic"""
    
    def __init__(self):
        self.db = Database()
        self.current_user: Optional[User] = None
        self.cart = Cart()
    
    def register_user(self, username: str, name: str, password: str) -> Tuple[bool, str]:
        """Register new user"""
        if not username or not name or not password:
            return False, "All fields are required"
        
        username = username.lower()
        if username in self.db.data["users"]:
            return False, "Username already exists"
        
        user = User(username, name, password)
        self.db.data["users"][username] = user.to_dict()
        self.db.log_activity("user_registered", username)
        self.db.save()
        return True, "Account created successfully"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Login user"""
        username = username.lower()
        user_data = self.db.data["users"].get(username)
        
        if not user_data:
            return False, "User not found"
        
        user = User.from_dict(username, user_data)
        if not user.verify_password(password):
            return False, "Invalid password"
        
        self.current_user = user
        self.db.log_activity("user_login", username)
        self.db.save()
        return True, f"Welcome back, {user.name}!"
    
    def logout_user(self) -> None:
        """Logout current user"""
        if self.current_user:
            self.db.log_activity("user_logout", self.current_user.username)
            self.db.save()
            self.current_user = None
            self.cart.clear()
    
    def get_restaurants(self) -> List[Tuple[str, Restaurant]]:
        """Get all restaurants"""
        restaurants = []
        for name, data in self.db.data["restaurants"].items():
            restaurants.append((name, Restaurant.from_dict(name, data)))
        return restaurants
    
    def get_restaurant(self, name: str) -> Optional[Restaurant]:
        """Get restaurant by name"""
        data = self.db.data["restaurants"].get(name)
        if data:
            return Restaurant.from_dict(name, data)
        return None
    
    def add_to_cart(self, restaurant_name: str, item_number: str, quantity: int = 1) -> Tuple[bool, str]:
        """Add item to cart"""
        restaurant = self.get_restaurant(restaurant_name)
        if not restaurant:
            return False, "Restaurant not found"
        
        item = restaurant.get_item(item_number)
        if not item:
            return False, "Item not found"
        
        if not item.is_available:
            return False, f"{item.name} is sold out"
        
        if self.cart.add_item(item, restaurant_name, quantity):
            return True, f"{item.name} added to cart"
        return False, "Not enough stock"
    
    def place_order(self, coupon_code: str = "") -> Tuple[bool, str, Optional[Order]]:
        """Place order"""
        if not self.current_user:
            return False, "Please login first", None
        
        if not self.cart.items:
            return False, "Cart is empty", None
        
        total = self.cart.total
        discount = 0
        coupon_applied = None
        
        if coupon_code:
            for coupon_data in self.db.data.get("coupons", []):
                if coupon_data["code"].upper() == coupon_code.upper():
                    coupon = Coupon(coupon_data["code"], coupon_data["type"], 
                                   coupon_data["value"], coupon_data["description"])
                    total, discount = coupon.apply(total)
                    coupon_applied = coupon.code
                    break
        
        user_data = self.db.data["users"][self.current_user.username]
        if user_data["wallet"] < total:
            return False, "Insufficient wallet balance", None
        
        order_id = f"ALD{self.db.data['next_order_id']}"
        self.db.data["next_order_id"] += 1
        
        order = Order(order_id, self.current_user.username, 
                     self.cart.to_list(), total)
        
        user_data["wallet"] -= total
        points = total // 10
        user_data["food_points"] = user_data.get("food_points", 0) + points
        
        self._update_stock_after_order()
        
        self.db.data["orders"].append(order.to_dict())
        user_data.setdefault("orders", []).append(order_id)
        
        self.db.log_activity("order_placed", self.current_user.username, 
                            f"Order {order_id} for ₹{total}")
        self.db.save()
        
        receipt_file = self.generate_receipt(order)
        
        self.cart.clear()
        return True, f"Order placed successfully! Receipt: {receipt_file}", order
    
    def _update_stock_after_order(self):
        """Decrease stock for ordered items"""
        for cart_item in self.cart.items:
            restaurant_data = self.db.data["restaurants"].get(cart_item.restaurant)
            if restaurant_data:
                for item in restaurant_data["menu"].values():
                    if item["name"] == cart_item.name:
                        item["stock"] = max(0, item["stock"] - cart_item.quantity)
                        if item["stock"] <= 0:
                            item["sold_out"] = True
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Cancel order with refund"""
        if not self.current_user:
            return False, "Please login first"
        
        for order_data in self.db.data["orders"]:
            if order_data["id"] == order_id and order_data["username"] == self.current_user.username:
                if order_data["status"] in ["Delivered", "Cancelled"]:
                    return False, "Order cannot be cancelled"
                
                user_data = self.db.data["users"][self.current_user.username]
                user_data["wallet"] += order_data["total"]
                
                self._restore_stock_after_cancel(order_data["items"])
                
                order_data["status"] = "Cancelled"
                self.db.log_activity("order_cancelled", self.current_user.username, 
                                    f"Order {order_id} cancelled")
                self.db.save()
                return True, "Order cancelled and refunded"
        
        return False, "Order not found"
    
    def _restore_stock_after_cancel(self, items: List[Dict]):
        """Restore stock after cancellation"""
        for item in items:
            restaurant_data = self.db.data["restaurants"].get(item["restaurant"])
            if restaurant_data:
                for menu_item in restaurant_data["menu"].values():
                    if menu_item["name"] == item["name"]:
                        menu_item["stock"] += item["quantity"]
                        menu_item["sold_out"] = False
    
    def book_seats(self, restaurant_name: str, seats: int) -> Tuple[bool, str]:
        """Book seats"""
        if not self.current_user:
            return False, "Please login first"
        
        restaurant_data = self.db.data["restaurants"].get(restaurant_name)
        if not restaurant_data:
            return False, "Restaurant not found"
        
        if seats <= 0:
            return False, "Invalid seat count"
        
        if seats > restaurant_data["available_seats"]:
            return False, "Not enough seats available"
        
        reservation_id = f"RES{self.db.data['next_reservation_id']}"
        self.db.data["next_reservation_id"] += 1
        
        reservation = Reservation(reservation_id, self.current_user.username, 
                                  restaurant_name, seats)
        
        restaurant_data["available_seats"] -= seats
        self.db.data.setdefault("reservations", []).append(reservation.to_dict())
        self.db.data["users"][self.current_user.username].setdefault("reservations", []).append(reservation_id)
        
        self.db.log_activity("reservation_made", self.current_user.username, 
                            f"Reservation {reservation_id} at {restaurant_name}")
        self.db.save()
        return True, f"Reservation confirmed! ID: {reservation_id}"
    
    def cancel_reservation(self, reservation_id: str) -> Tuple[bool, str]:
        """Cancel reservation"""
        if not self.current_user:
            return False, "Please login first"
        
        for reservation_data in self.db.data.get("reservations", []):
            if reservation_data["id"] == reservation_id and reservation_data["username"] == self.current_user.username:
                if reservation_data["status"] == "Cancelled":
                    return False, "Reservation already cancelled"
                
                restaurant_data = self.db.data["restaurants"].get(reservation_data["restaurant"])
                if restaurant_data:
                    restaurant_data["available_seats"] = min(
                        restaurant_data["total_seats"],
                        restaurant_data["available_seats"] + reservation_data["seats"]
                    )
                
                reservation_data["status"] = "Cancelled"
                self.db.log_activity("reservation_cancelled", self.current_user.username,
                                    f"Reservation {reservation_id} cancelled")
                self.db.save()
                return True, "Reservation cancelled"
        
        return False, "Reservation not found"
    
    def add_review(self, restaurant_name: str, rating: int, comment: str) -> Tuple[bool, str]:
        """Add review"""
        if not self.current_user:
            return False, "Please login first"
        
        if not 1 <= rating <= 5:
            return False, "Rating must be between 1 and 5"
        
        review = Review(self.current_user.username, restaurant_name, rating, comment)
        self.db.data.setdefault("reviews", []).append(review.to_dict())
        self.db.data["users"][self.current_user.username].setdefault("reviews", []).append(review.to_dict())
        
        self.db.log_activity("review_added", self.current_user.username,
                            f"Review for {restaurant_name}")
        self.db.save()
        return True, "Review added successfully"
    
    def generate_receipt(self, order: Order) -> str:
        """Generate receipt file"""
        os.makedirs(RECEIPT_DIR, exist_ok=True)
        filename = f"receipt_{order.id}.txt"
        path = os.path.join(RECEIPT_DIR, filename)
        
        lines = []
        lines.append("=" * 50)
        lines.append("ALAKH DA DHAABA - ORDER RECEIPT")
        lines.append("=" * 50)
        lines.append(f"Order ID: {order.id}")
        lines.append(f"Date: {order.date}")
        lines.append(f"Customer: {order.username}")
        lines.append("-" * 50)
        lines.append("ITEMS:")
        
        for item in order.items:
            lines.append(f"  {item['name']} x{item['quantity']} = ₹{item['price'] * item['quantity']}")
        
        lines.append("-" * 50)
        lines.append(f"TOTAL: ₹{order.total}")
        lines.append(f"STATUS: {order.status}")
        lines.append("=" * 50)
        lines.append("Thank you for your order!")
        
        with open(path, "w") as f:
            f.write("\n".join(lines))
        
        return path
    
    def get_revenue_stats(self) -> Dict:
        """Get revenue statistics"""
        orders = self.db.data.get("orders", [])
        total_revenue = sum(order["total"] for order in orders if order["status"] != "Cancelled")
        total_orders = len(orders)
        avg_order = total_revenue // total_orders if total_orders > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order": avg_order
        }