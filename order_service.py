"""Order workflows for the food-court service."""

import os
from typing import Dict, List, Optional, Tuple

from models import Coupon, Order
from config import POINTS_PER_RUPEE, RECEIPT_DIR


class OrderServiceMixin:
    """Order placement, cancellation, fulfillment, and receipts."""

    def place_order(self, coupon_code: str = "") -> Tuple[bool, str, Optional[Order]]:
        """Place the current user's cart order after validating stock and funds."""
        if not self.current_user:
            return False, "Please login first", None
        if not self.cart.items:
            return False, "Cart is empty", None

        total = self.cart.total
        if coupon_code:
            coupon_data = next(
                (data for data in self.db.data.get("coupons", [])
                 if data.get("code", "").upper() == coupon_code.upper()),
                None,
            )
            if coupon_data is None:
                return False, "Coupon code not found", None
            used_by = coupon_data.setdefault("used_by", [])
            if self.current_user.username in used_by:
                return False, "You have already used this coupon", None
            coupon = Coupon(
                coupon_data["code"], coupon_data["type"],
                coupon_data["value"], coupon_data.get("description", ""),
            )
            total, _ = coupon.apply(total)

        for cart_item in self.cart.items:
            menu_item = self._find_menu_item(cart_item.restaurant, cart_item.item_number, cart_item.name)
            if menu_item is None or menu_item.get("stock", 0) < cart_item.quantity:
                return False, f"Not enough stock for {cart_item.name}", None

        user_data = self.db.data["users"][self.current_user.username]
        if user_data.get("wallet", 0) < total:
            return False, "Insufficient wallet balance", None

        order_id = f"ALD{self.db.data['next_order_id']}"
        self.db.data["next_order_id"] += 1
        order = Order(order_id, self.current_user.username, self.cart.to_list(), total)
        order_data = order.to_dict()
        order_data["order_id"] = order_id
        order_data["user_id"] = user_data.get("user_id")
        for item_data in order_data["items"]:
            menu_item = self._find_menu_item(item_data["restaurant"], item_data.get("item_number", ""), item_data["name"])
            restaurant_data = self.db.data.get("restaurants", {}).get(item_data["restaurant"], {})
            item_data["restaurant_id"] = restaurant_data.get("restaurant_id")
            if menu_item is not None:
                item_data["food_id"] = menu_item.get("food_id")
        if coupon_code:
            coupon_data["used_by"].append(self.current_user.username)
            order_data["coupon_code"] = coupon_data["code"].upper()
        user_data["wallet"] -= total
        user_data["food_points"] = user_data.get("food_points", 0) + total // POINTS_PER_RUPEE
        self._update_stock_after_order()
        self.db.data["orders"].append(order_data)
        user_data.setdefault("orders", []).append(order_id)
        self.db.log_activity("order_placed", self.current_user.username, f"Order {order_id} for ₹{total}")
        self.db.save()
        receipt_file = self.generate_receipt(order)
        self.cart.clear()
        return True, f"Order placed successfully! Receipt: {receipt_file}", order

    def _find_menu_item(self, restaurant_name: str, item_number: str, item_name: str) -> Optional[Dict]:
        """Find an item by stable key, falling back for legacy order records."""
        restaurant = self.db.data.get("restaurants", {}).get(restaurant_name, {})
        menu = restaurant.get("menu", {})
        return menu.get(item_number) or next(
            (item for item in menu.values() if item.get("name") == item_name), None
        )

    def _update_stock_after_order(self) -> None:
        """Decrease stock for each ordered item."""
        for cart_item in self.cart.items:
            item = self._find_menu_item(cart_item.restaurant, cart_item.item_number, cart_item.name)
            if item is not None:
                item["stock"] = max(0, item.get("stock", 0) - cart_item.quantity)
                item["sold_out"] = item["stock"] <= 0

    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Cancel the current user's order and issue a one-time refund."""
        if not self.current_user:
            return False, "Please login first"
        for order_data in self.db.data.get("orders", []):
            if order_data.get("id") == order_id and order_data.get("username") == self.current_user.username:
                if order_data.get("status") in {"Delivered", "Cancelled"}:
                    return False, "Order cannot be cancelled"
                self._refund_order(order_data)
                self.db.log_activity("order_cancelled", self.current_user.username, f"Order {order_id} cancelled")
                self.db.save()
                return True, "Order cancelled and refunded"
        return False, "Order not found"

    def _refund_order(self, order_data: Dict) -> None:
        """Refund an order once and restore its stock."""
        if order_data.get("refunded"):
            return
        user_data = self.db.data.get("users", {}).get(order_data.get("username"))
        if user_data is not None:
            user_data["wallet"] = user_data.get("wallet", 0) + order_data.get("total", 0)
            if self.current_user and self.current_user.username == order_data.get("username"):
                self.current_user.wallet = user_data["wallet"]
        self._restore_stock_after_cancel(order_data.get("items", []))
        order_data["status"] = "Cancelled"
        order_data["refunded"] = True

    def update_order_status(self, order_id: str, new_status: str) -> Tuple[bool, str]:
        """Advance an order through its allowed fulfillment states."""
        if new_status not in {"Preparing", "Confirmed", "Ready", "Delivered", "Cancelled"}:
            return False, "Invalid order status"
        for order_data in self.db.data.get("orders", []):
            if order_data.get("id") != order_id:
                continue
            current_status = order_data.get("status")
            if current_status in {"Cancelled", "Delivered"}:
                return False, f"{current_status} orders cannot be updated"
            if new_status == "Cancelled":
                self._refund_order(order_data)
                self.db.log_activity("order_cancelled", "admin", f"Order {order_id} cancelled")
            elif new_status != current_status and new_status not in Order.STATUS_FLOW.get(current_status, []):
                return False, f"Cannot move {current_status} to {new_status}"
            else:
                order_data["status"] = new_status
                self.db.log_activity("order_status_updated", "admin", f"Order {order_id} set to {new_status}")
            self.db.save()
            return True, f"Order {order_id} updated to {new_status}"
        return False, "Order not found"

    def update_order_item_quantity(self, order_id: str, item_index: int, quantity: int) -> Tuple[bool, str]:
        """Edit an active order item while reconciling stock and wallet funds."""
        if quantity <= 0:
            return False, "Quantity must be greater than zero"
        for order_data in self.db.data.get("orders", []):
            if order_data.get("id") != order_id:
                continue
            if order_data.get("status") in {"Delivered", "Cancelled"}:
                return False, "Delivered and cancelled orders cannot be edited"
            items = order_data.get("items", [])
            if not 0 <= item_index < len(items):
                return False, "Invalid order item"
            item = items[item_index]
            old_quantity = item.get("quantity", 0)
            change = quantity - old_quantity
            menu_item = self._find_menu_item(item.get("restaurant", ""), item.get("item_number", ""), item.get("name", ""))
            user_data = self.db.data.get("users", {}).get(order_data.get("username"))
            if menu_item is None:
                return False, "The original menu item is no longer available"
            price_change = change * item.get("price", 0)
            if change > 0 and menu_item.get("stock", 0) < change:
                return False, "Not enough stock for the new quantity"
            if price_change > 0 and (not user_data or user_data.get("wallet", 0) < price_change):
                return False, "Customer wallet cannot cover the price difference"
            menu_item["stock"] = max(0, menu_item.get("stock", 0) - change)
            menu_item["sold_out"] = menu_item["stock"] <= 0
            if user_data is not None:
                user_data["wallet"] = user_data.get("wallet", 0) - price_change
            item["quantity"] = quantity
            order_data["total"] = order_data.get("total", 0) + price_change
            self.db.log_activity("order_item_updated", "admin", f"Order {order_id}: {item.get('name', 'item')} x{quantity}")
            self.db.save()
            return True, f"{item.get('name', 'Item')} quantity updated to {quantity}"
        return False, "Order not found"

    def _restore_stock_after_cancel(self, items: List[Dict]) -> None:
        """Restore stock for cancelled order items."""
        for item in items:
            menu_item = self._find_menu_item(item.get("restaurant", ""), item.get("item_number", ""), item.get("name", ""))
            if menu_item is not None:
                menu_item["stock"] = menu_item.get("stock", 0) + item.get("quantity", 0)
                menu_item["sold_out"] = False

    def generate_receipt(self, order: Order) -> str:
        """Generate and save a text receipt for an order."""
        os.makedirs(RECEIPT_DIR, exist_ok=True)
        path = os.path.join(RECEIPT_DIR, f"receipt_{order.id}.txt")
        lines = ["=" * 50, "ALAKH DA DHAABA - ORDER RECEIPT", "=" * 50,
                 f"Order ID: {order.id}", f"Date: {order.date}", f"Customer: {order.username}",
                 "-" * 50, "ITEMS:"]
        lines.extend(f"  {item['name']} x{item['quantity']} = ₹{item['price'] * item['quantity']}" for item in order.items)
        lines.extend(["-" * 50, f"TOTAL: ₹{order.total}", f"STATUS: {order.status}", "=" * 50, "Thank you for your order!"])
        with open(path, "w", encoding="utf-8") as receipt:
            receipt.write("\n".join(lines))
        return path
