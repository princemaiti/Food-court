import unittest
from types import SimpleNamespace

from models import Cart, Coupon, FoodItem, User
from services import FoodCourtService


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


class CouponTests(unittest.TestCase):
    def test_discount_cannot_exceed_total(self):
        coupon = Coupon("BIG", "flat", 500)

        discounted_total, discount = coupon.apply(200)

        self.assertEqual(discounted_total, 0)
        self.assertEqual(discount, 200)


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

    def test_order_status_must_follow_flow(self):
        success, _ = self.service.update_order_status("ALD1", "Delivered")

        self.assertFalse(success)
        self.assertEqual(self.database.data["orders"][0]["status"], "Preparing")

    def test_order_status_can_advance(self):
        success, _ = self.service.update_order_status("ALD1", "Confirmed")

        self.assertTrue(success)
        self.assertEqual(self.database.data["orders"][0]["status"], "Confirmed")


if __name__ == "__main__":
    unittest.main()
