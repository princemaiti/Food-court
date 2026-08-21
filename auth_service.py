"""Authentication workflows for the food-court service."""

from typing import Optional, Tuple

from models import User


class AuthServiceMixin:
    """Registration and session management operations."""

    def register_user(self, username: str, name: str, password: str) -> Tuple[bool, str]:
        """Register a new user account."""
        if not username or not name or not password:
            return False, "All fields are required"
        if len(username.strip()) < 3 or len(password) < 6:
            return False, "Username must have 3+ characters and password 6+ characters"

        username = username.strip().lower()
        name = name.strip()
        if username in self.db.data["users"]:
            return False, "Username already exists"

        user = User(username, name, password)
        self.db.data["users"][username] = user.to_dict()
        self.db.log_activity("user_registered", username)
        self.db.save()
        return True, "Account created successfully"

    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user and migrate legacy password hashes."""
        username = username.lower()
        user_data = self.db.data["users"].get(username)
        if not user_data:
            return False, "User not found"

        user = User.from_dict(username, user_data)
        if not user.verify_password(password):
            return False, "Invalid password"

        user_data["password"] = user.password_hash
        self.current_user = user
        self.db.log_activity("user_login", username)
        self.db.save()
        return True, f"Welcome back, {user.name}!"

    def logout_user(self) -> None:
        """Log out the current user and clear their cart."""
        if self.current_user:
            self.db.log_activity("user_logout", self.current_user.username)
            self.db.save()
            self.current_user = None
            self.cart.clear()