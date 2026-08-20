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
