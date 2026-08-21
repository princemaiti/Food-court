"""User portal navigation for the terminal application."""

from ui import C, clear_screen, error, header, menu_box, money, pause, success


class UserPortalMixin:
    """Navigation loop for authenticated users."""

    def user_portal(self):
        """Run the user portal until logout."""
        while True:
            clear_screen()
            user = self.service.current_user
            if not user:
                return

            header("USER PORTAL", "👤")
            print(f"\nWelcome, {C.BOLD}{user.name}{C.RESET}! 👋")
            print(f"💰 Wallet: {money(user.wallet)}   ⭐ Points: {C.YELLOW}{user.food_points}{C.RESET}")
            print()
            menu_box([
                ("1", "🍔 Browse Food"), ("2", "🏪 Restaurants"), ("3", "🛒 Cart"),
                ("4", "🪑 Book Seats"), ("5", "📅 My Reservations"), ("6", "📦 My Orders"),
                ("7", "❤️ Favorites"), ("8", "💰 Wallet"), ("9", "⭐ Reviews"),
                ("10", "🔔 Notifications"), ("11", "👤 Profile"), ("12", "🚪 Logout"),
            ])
            choice = input(f"\n{C.CYAN}Enter your choice: {C.RESET}").strip()
            screens = {
                "1": self.browse_food, "2": self.restaurants_screen,
                "3": self.cart_screen, "4": self.book_seats_screen,
                "5": self.my_reservations_screen, "6": self.my_orders_screen,
                "7": self.favorites_screen, "8": self.wallet_screen,
                "9": self.reviews_screen, "10": self.notifications_screen,
                "11": self.profile_screen,
            }
            if choice in screens:
                screens[choice]()
            elif choice == "12":
                self.service.logout_user()
                success("Logged out successfully!")
                pause()
                return
            else:
                error("Invalid choice.")
                pause()