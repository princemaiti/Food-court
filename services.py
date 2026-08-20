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

    def add_favorite(self, restaurant_name: str, item_number: str) -> Tuple[bool, str]:
        """Save a menu item to the current user's favorites"""
        if not self.current_user:
            return False, "Please login first"

        restaurant = self.get_restaurant(restaurant_name)
        if not restaurant:
            return False, "Restaurant not found"

        item = restaurant.get_item(item_number)
        if not item:
            return False, "Item not found"

        favorite = {
            "name": item.name,
            "price": item.price,
            "restaurant": restaurant_name,
            "item_number": item_number,
        }
        if any(
            saved.get("restaurant") == restaurant_name
            and saved.get("item_number") == item_number
            for saved in self.current_user.favorites
        ):
            return False, "Item is already in favorites"

        self.current_user.favorites.append(favorite)
        self.db.data["users"][self.current_user.username]["favorites"] = self.current_user.favorites
        self.db.save()
        return True, f"{item.name} added to favorites"

    def remove_favorite(self, favorite_index: int) -> Tuple[bool, str]:
        """Remove a saved favorite by its displayed index"""
        if not self.current_user:
            return False, "Please login first"

        if not 0 <= favorite_index < len(self.current_user.favorites):
            return False, "Invalid favorite number"

        removed = self.current_user.favorites.pop(favorite_index)
        self.db.data["users"][self.current_user.username]["favorites"] = self.current_user.favorites
        self.db.save()
        return True, f"{removed.get('name', 'Item')} removed from favorites"
    
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

    def update_order_status(self, order_id: str, new_status: str) -> Tuple[bool, str]:
        """Update an order status from the admin portal"""
        valid_statuses = {"Preparing", "Confirmed", "Ready", "Delivered", "Cancelled"}
        if new_status not in valid_statuses:
            return False, "Invalid order status"

        for order_data in self.db.data.get("orders", []):
            if order_data["id"] != order_id:
                continue
            if order_data["status"] in {"Cancelled", "Delivered"}:
                return False, "Completed orders cannot be updated"
            if new_status != order_data["status"] and new_status not in Order.STATUS_FLOW.get(order_data["status"], []):
                return False, f"Cannot move {order_data['status']} to {new_status}"

            order_data["status"] = new_status
            self.db.log_activity("order_status_updated", "admin", f"Order {order_id} set to {new_status}")
            self.db.save()
            return True, f"Order {order_id} updated to {new_status}"

        return False, "Order not found"

    def set_available_seats(self, restaurant_name: str, available_seats: int) -> Tuple[bool, str]:
        """Set the available seats for a restaurant"""
        restaurant = self.db.data.get("restaurants", {}).get(restaurant_name)
        if not restaurant:
            return False, "Restaurant not found"
        if not 0 <= available_seats <= restaurant.get("total_seats", 0):
            return False, "Available seats are outside the valid range"

        restaurant["available_seats"] = available_seats
        self.db.log_activity("seats_updated", "admin", f"{restaurant_name}: {available_seats} seats available")
        self.db.save()
        return True, f"Seats updated for {restaurant_name}"
    
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

    def update_user(self, username: str, name: str, wallet: int, food_points: int) -> Tuple[bool, str]:
        """Update editable admin fields for a user"""
        user_data = self.db.data.get("users", {}).get(username)
        if not user_data:
            return False, "User not found"
        if not name.strip() or wallet < 0 or food_points < 0:
            return False, "Name must be set and numeric values cannot be negative"

        user_data["name"] = name.strip()
        user_data["wallet"] = wallet
        user_data["food_points"] = food_points
        if self.current_user and self.current_user.username == username:
            self.current_user.name = user_data["name"]
            self.current_user.wallet = wallet
            self.current_user.food_points = food_points
        self.db.log_activity("user_updated", "admin", f"User {username} updated")
        self.db.save()
        return True, f"User {username} updated"

    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user while retaining historical order data"""
        if username not in self.db.data.get("users", {}):
            return False, "User not found"
        if self.current_user and self.current_user.username == username:
            return False, "The logged-in admin cannot delete the active user"

        del self.db.data["users"][username]
        self.db.log_activity("user_deleted", "admin", f"User {username} deleted")
        self.db.save()
        return True, f"User {username} deleted"

    def delete_review(self, review_index: int) -> Tuple[bool, str]:
        """Delete a review from the global and user-specific collections"""
        reviews = self.db.data.get("reviews", [])
        if not 0 <= review_index < len(reviews):
            return False, "Invalid review number"

        review = reviews.pop(review_index)
        user_reviews = self.db.data.get("users", {}).get(review.get("username"), {}).get("reviews", [])
        for index, user_review in enumerate(user_reviews):
            if user_review == review:
                user_reviews.pop(index)
                break
        self.db.log_activity("review_deleted", "admin", f"Review by {review.get('username', 'unknown')} deleted")
        self.db.save()
        return True, "Review deleted"

    def add_restaurant(self, name: str, emoji: str, total_seats: int) -> Tuple[bool, str]:
        """Add a restaurant branch"""
        name = name.strip()
        if not name or name in self.db.data.get("restaurants", {}):
            return False, "Restaurant name is empty or already exists"
        if total_seats <= 0:
            return False, "Seats must be greater than zero"

        self.db.data.setdefault("restaurants", {})[name] = {
            "emoji": emoji.strip() or "🍽️",
            "total_seats": total_seats,
            "available_seats": total_seats,
            "menu": {},
        }
        self.db.log_activity("restaurant_added", "admin", f"Restaurant {name} added")
        self.db.save()
        return True, f"Restaurant {name} added"

    def remove_restaurant(self, name: str) -> Tuple[bool, str]:
        """Remove a restaurant branch without touching historical orders"""
        if name not in self.db.data.get("restaurants", {}):
            return False, "Restaurant not found"
        if any(order.get("status") not in {"Delivered", "Cancelled"} and any(
            item.get("restaurant") == name for item in order.get("items", [])
        ) for order in self.db.data.get("orders", [])):
            return False, "Restaurant has an active order and cannot be removed"

        del self.db.data["restaurants"][name]
        self.db.log_activity("restaurant_deleted", "admin", f"Restaurant {name} deleted")
        self.db.save()
        return True, f"Restaurant {name} removed"

    def add_menu_item(self, restaurant_name: str, item: Dict) -> Tuple[bool, str]:
        """Add a food item to a restaurant menu"""
        restaurant = self.db.data.get("restaurants", {}).get(restaurant_name)
        if not restaurant:
            return False, "Restaurant not found"
        if item["price"] <= 0 or item["stock"] < 0 or not item["name"].strip():
            return False, "Food name, price, and stock values are invalid"

        numbers = [int(number) for number in restaurant.get("menu", {}) if str(number).isdigit()]
        item_number = str(max(numbers, default=0) + 1)
        item["sold_out"] = item["stock"] <= 0
        restaurant.setdefault("menu", {})[item_number] = item
        self.db.log_activity("menu_item_added", "admin", f"{item['name']} added to {restaurant_name}")
        self.db.save()
        return True, f"{item['name']} added as item {item_number}"

    def remove_menu_item(self, restaurant_name: str, item_number: str) -> Tuple[bool, str]:
        """Remove a food item while preserving old order snapshots"""
        menu = self.db.data.get("restaurants", {}).get(restaurant_name, {}).get("menu", {})
        if item_number not in menu:
            return False, "Food item not found"
        item_name = menu[item_number].get("name", "Food item")
        del menu[item_number]
        self.db.log_activity("menu_item_deleted", "admin", f"{item_name} removed from {restaurant_name}")
        self.db.save()
        return True, f"{item_name} removed"

    def add_announcement(self, message: str) -> Tuple[bool, str]:
        """Publish an announcement"""
        message = message.strip()
        if not message:
            return False, "Announcement cannot be empty"
        self.db.data.setdefault("announcements", []).append(message)
        self.db.log_activity("announcement_added", "admin", message)
        self.db.save()
        return True, "Announcement published"

    def remove_announcement(self, announcement_index: int) -> Tuple[bool, str]:
        """Remove an announcement by displayed index"""
        announcements = self.db.data.get("announcements", [])
        if not 0 <= announcement_index < len(announcements):
            return False, "Invalid announcement number"
        announcements.pop(announcement_index)
        self.db.log_activity("announcement_deleted", "admin")
        self.db.save()
        return True, "Announcement removed"
    
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
        active_orders = [order for order in orders if order.get("status") != "Cancelled"]
        total_revenue = sum(order.get("total", 0) for order in active_orders)
        total_orders = len(active_orders)
        avg_order = total_revenue // total_orders if total_orders else 0
        status_counts = {}
        top_items = {}
        restaurant_revenue = {}
        for order in orders:
            status = order.get("status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            if status == "Cancelled":
                continue
            for item in order.get("items", []):
                name = item.get("name", "Unknown item")
                quantity = item.get("quantity", 0)
                top_items[name] = top_items.get(name, 0) + quantity
                restaurant = item.get("restaurant", "Unknown restaurant")
                restaurant_revenue[restaurant] = restaurant_revenue.get(restaurant, 0) + item.get("price", 0) * quantity
        
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order": avg_order,
            "cancelled_orders": status_counts.get("Cancelled", 0),
            "status_counts": status_counts,
            "top_items": sorted(top_items.items(), key=lambda entry: entry[1], reverse=True)[:5],
            "restaurant_revenue": sorted(restaurant_revenue.items(), key=lambda entry: entry[1], reverse=True),
            "user_count": len(self.db.data.get("users", {})),
            "restaurant_count": len(self.db.data.get("restaurants", {})),
            "review_count": len(self.db.data.get("reviews", [])),
        }