import unittest
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from models import Cart, Coupon, FoodItem, Restaurant, User
from services import FoodCourtService
from ui import C, _menu_label, _visible_length, announcement_card, menu_box, panel, restaurant_card


class FakeDatabase:
    def __init__(self, data):
        self.data = data
        self.saved = 0
        self.logs = []

    def save(self):
        self.saved += 1

    def log_activity(self, action, username="system", details=""):
        self.logs.append((action, username, details))


class CartTests(unittest.TestCase):
    def test_rejects_non_positive_quantity(self):
        cart = Cart()
        item = FoodItem("Soup", 80, stock=5)

        self.assertFalse(cart.add_item(item, "Cafe", 0))
        self.assertFalse(cart.add_item(item, "Cafe", -1))
        self.assertEqual(cart.items, [])

    def test_removing_with_zero_quantity(self):
        cart = Cart()
        item = FoodItem("Soup", 80, stock=5)
        cart.add_item(item, "Cafe", 2)

        self.assertTrue(cart.update_quantity(0, 0))
        self.assertEqual(cart.items, [])

    def test_cannot_change_quantity_above_available_stock(self):
        cart = Cart()
        item = FoodItem("Soup", 80, stock=3)
        cart.add_item(item, "Cafe", 2, "1")

        self.assertFalse(cart.update_quantity(0, 4))
        self.assertEqual(cart.items[0].quantity, 2)
        self.assertTrue(cart.update_quantity(0, 3))
        self.assertEqual(cart.items[0].quantity, 3)

    def test_same_named_items_from_different_menu_entries_stay_separate(self):
        cart = Cart()
        first = FoodItem("Special", 80, stock=5)
        second = FoodItem("Special", 120, stock=5)

        self.assertTrue(cart.add_item(first, "Cafe", 1, "1"))
        self.assertTrue(cart.add_item(second, "Cafe", 1, "2"))

        self.assertEqual(len(cart.items), 2)
        self.assertEqual(cart.total, 200)


class UITests(unittest.TestCase):
    def test_emoji_width_ignores_ansi_and_zero_width_marks(self):
        self.assertEqual(_visible_length(f" {C.YELLOW}1.{C.RESET} 🍔 Browse Food"), 18)
        self.assertEqual(_visible_length("❤️"), 2)
        self.assertEqual(_visible_length("👨‍🍳"), 2)

    def test_menu_labels_have_consistent_icon_spacing(self):
        self.assertEqual(_menu_label("🍔 Browse Food"), "🍔  Browse Food")
        self.assertEqual(_menu_label("Logout"), "Logout")
        self.assertEqual(_menu_label("Manage Users"), "Manage Users")

    def test_menu_box_rows_keep_their_border_alignment(self):
        output = StringIO()
        with patch("ui.get_width", return_value=40), patch("sys.stdout", output):
            menu_box([("1", "🍔 Browse Food"), ("2", "Logout")])

        rows = output.getvalue().splitlines()
        self.assertTrue(all(_visible_length(row) == 40 for row in rows))

    def test_restaurant_metadata_survives_model_loading(self):
        restaurant = Restaurant.from_dict("Cafe", {
            "emoji": "🍵",
            "total_seats": 12,
            "cuisine": "Cafe",
            "description": "Fresh drinks and snacks",
            "opening_hours": "9:00 AM - 9:00 PM",
            "service_style": "Counter service",
        })

        self.assertEqual(restaurant.cuisine, "Cafe")
        self.assertEqual(restaurant.opening_hours, "9:00 AM - 9:00 PM")
        self.assertEqual(restaurant.service_style, "Counter service")

    def test_restaurant_and_announcement_cards_keep_their_width(self):
        output = StringIO()
        with patch("ui.get_width", return_value=40), patch("sys.stdout", output):
            restaurant_card(1, "Cafe", "🍵", "Cafe", "9:00 AM - 9:00 PM", "Takeaway", "8/12", "Fresh drinks")
            announcement_card(1, "Welcome to the food court")

        bordered_lines = [line for line in output.getvalue().splitlines() if "│" in line or "┌" in line or "└" in line]
        self.assertTrue(all(_visible_length(line) == 40 for line in bordered_lines))

    def test_panel_rows_keep_their_width_with_emoji_and_long_text(self):
        output = StringIO()
        with patch("ui.get_width", return_value=40), patch("sys.stdout", output):
            panel("📢  NOTIFICATIONS", ["A very long notification that must fit"])

        bordered_lines = output.getvalue().splitlines()
        self.assertTrue(all(_visible_length(line) == 40 for line in bordered_lines))


class CouponTests(unittest.TestCase):
    def test_discount_cannot_exceed_total(self):
        coupon = Coupon("BIG", "flat", 500)

        discounted_total, discount = coupon.apply(200)

        self.assertEqual(discounted_total, 0)
        self.assertEqual(discount, 200)

    def test_negative_discount_does_not_increase_total(self):
        coupon = Coupon("BAD", "flat", -50)

        discounted_total, discount = coupon.apply(200)

        self.assertEqual(discounted_total, 200)
        self.assertEqual(discount, 0)


class AuthenticationTests(unittest.TestCase):
    def test_passwords_are_salted_and_verifiable(self):
        first = User("one", "One", "same-password")
        second = User("two", "Two", "same-password")

        self.assertNotEqual(first.password_hash, second.password_hash)
        self.assertTrue(first.verify_password("same-password"))
        self.assertFalse(first.verify_password("wrong-password"))

    def test_legacy_sha256_hash_is_migrated_after_login(self):
        import hashlib

        user = User.from_dict("legacy", {
            "name": "Legacy",
            "password": hashlib.sha256(b"old-password").hexdigest(),
        })

        self.assertTrue(user.verify_password("old-password"))
        self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$"))

    def test_login_persists_legacy_hash_upgrade(self):
        import hashlib

        legacy_data = {
            "name": "Legacy",
            "password": hashlib.sha256(b"old-password").hexdigest(),
            "wallet": 100,
        }
        database = FakeDatabase({"users": {"legacy": legacy_data}})
        service = FoodCourtService.__new__(FoodCourtService)
        service.db = database
        service.current_user = None

        success, _ = service.login_user("legacy", "old-password")

        self.assertTrue(success)
        self.assertTrue(database.data["users"]["legacy"]["password"].startswith("pbkdf2_sha256$"))


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.user = User("tester", "Test User", "password", 100)
        self.database = FakeDatabase({
            "users": {"tester": self.user.to_dict()},
            "orders": [{
                "id": "ALD1",
                "username": "tester",
                "total": 100,
                "status": "Preparing",
                "items": [],
            }],
            "restaurants": {},
            "reviews": [],
            "announcements": [],
            "coupons": [],
            "next_order_id": 1001,
        })
        self.service = FoodCourtService.__new__(FoodCourtService)
        self.service.db = self.database
        self.service.current_user = self.user
        self.service.cart = Cart()

    def test_wallet_top_up_persists_and_updates_session(self):
        success, message = self.service.add_wallet_money(50)

        self.assertTrue(success)
        self.assertIn("Added", message)
        self.assertEqual(self.user.wallet, 150)
        self.assertEqual(self.database.data["users"]["tester"]["wallet"], 150)
        self.assertEqual(self.database.saved, 1)

    def test_wallet_rejects_invalid_amount(self):
        success, message = self.service.add_wallet_money(0)

        self.assertFalse(success)
        self.assertIn("greater than zero", message)
        self.assertEqual(self.user.wallet, 100)
        self.assertEqual(self.database.saved, 0)

    def test_unknown_coupon_rejects_order(self):
        self.service.cart.add_item(FoodItem("Soup", 80, stock=5), "Cafe", 1, "1")

        success, message, order = self.service.place_order("UNKNOWN")

        self.assertFalse(success)
        self.assertIn("not found", message)
        self.assertIsNone(order)

    def test_coupon_can_only_be_used_once_by_each_user(self):
        self.database.data["restaurants"] = {
            "Cafe": {"menu": {"1": {"name": "Soup", "price": 80, "stock": 5}}},
        }
        self.database.data["coupons"] = [{
            "code": "ONCE", "type": "flat", "value": 10, "description": "One use",
        }]
        self.service.cart.add_item(FoodItem("Soup", 80, stock=5), "Cafe", 1, "1")

        first_success, _, _ = self.service.place_order("ONCE")
        self.service.cart.add_item(FoodItem("Soup", 80, stock=4), "Cafe", 1, "1")
        second_success, second_message, _ = self.service.place_order("ONCE")

        self.assertTrue(first_success)
        self.assertFalse(second_success)
        self.assertIn("already used", second_message)

    def test_order_status_must_follow_flow(self):
        success, _ = self.service.update_order_status("ALD1", "Delivered")

        self.assertFalse(success)
        self.assertEqual(self.database.data["orders"][0]["status"], "Preparing")

    def test_order_status_can_advance(self):
        success, _ = self.service.update_order_status("ALD1", "Confirmed")

        self.assertTrue(success)
        self.assertEqual(self.database.data["orders"][0]["status"], "Confirmed")

    def test_delivered_order_cannot_edit_item_quantity(self):
        self.database.data["orders"][0].update({
            "status": "Delivered",
            "items": [{"name": "Soup", "price": 80, "quantity": 1, "restaurant": "Cafe"}],
        })
        self.database.data["restaurants"] = {
            "Cafe": {"menu": {"1": {"name": "Soup", "price": 80, "stock": 4}}},
        }

        success, _ = self.service.update_order_item_quantity("ALD1", 0, 2)

        self.assertFalse(success)
        self.assertEqual(self.database.data["orders"][0]["items"][0]["quantity"], 1)

    def test_active_order_item_edit_updates_total_wallet_and_stock(self):
        self.database.data["orders"][0].update({
            "items": [{"name": "Soup", "price": 80, "quantity": 1, "restaurant": "Cafe", "item_number": "1"}],
        })
        self.database.data["restaurants"] = {
            "Cafe": {"menu": {"1": {"name": "Soup", "price": 80, "stock": 4}}},
        }

        success, _ = self.service.update_order_item_quantity("ALD1", 0, 2)

        self.assertTrue(success)
        self.assertEqual(self.database.data["orders"][0]["items"][0]["quantity"], 2)
        self.assertEqual(self.database.data["orders"][0]["total"], 180)
        self.assertEqual(self.database.data["users"]["tester"]["wallet"], 20)
        self.assertEqual(self.database.data["restaurants"]["Cafe"]["menu"]["1"]["stock"], 3)

    def test_admin_can_update_user_name_balance_and_points(self):
        success, _ = self.service.update_user("tester", "Updated User", 250, 40)

        self.assertTrue(success)
        self.assertEqual(self.database.data["users"]["tester"]["name"], "Updated User")
        self.assertEqual(self.database.data["users"]["tester"]["wallet"], 250)
        self.assertEqual(self.database.data["users"]["tester"]["food_points"], 40)

    def test_wallet_adjustment_requires_reason_and_records_transaction(self):
        success, _ = self.service.adjust_user_wallet("tester", 50, "Support credit")

        self.assertTrue(success)
        self.assertEqual(self.database.data["users"]["tester"]["wallet"], 150)
        self.assertEqual(self.database.data["users"]["tester"]["wallet_transactions"][0]["reason"], "Support credit")
        self.assertFalse(self.service.adjust_user_wallet("tester", -500, "Refund")[0])
        self.assertFalse(self.service.adjust_user_wallet("tester", 10, "")[0])

    def test_cancel_order_refunds_only_once(self):
        self.database.data["restaurants"] = {
            "Cafe": {
                "menu": {"1": {"name": "Soup", "stock": 0}},
            }
        }
        self.database.data["orders"][0].update({
            "total": 40,
            "items": [{"name": "Soup", "quantity": 1, "restaurant": "Cafe"}],
        })
        self.user.wallet = 60
        self.database.data["users"]["tester"]["wallet"] = 60

        first_success, _ = self.service.cancel_order("ALD1")
        second_success, _ = self.service.cancel_order("ALD1")

        self.assertTrue(first_success)
        self.assertFalse(second_success)
        self.assertEqual(self.user.wallet, 100)
        self.assertEqual(self.database.data["restaurants"]["Cafe"]["menu"]["1"]["stock"], 1)


if __name__ == "__main__":
    unittest.main()
