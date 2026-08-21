"""
Alakh Da Dhaaba - Main Entry Point
"""

from services import FoodCourtService
from ui import *
from config import ADMIN_PASSWORD, ADMIN_USERNAME
from user_portal import UserPortalMixin
from admin_portal import AdminPortalMixin
import sys

class FoodCourtApp(UserPortalMixin, AdminPortalMixin):
    """Main application"""
    
    def __init__(self):
        self.service = FoodCourtService()
    
    def run(self):
        """Run main loop"""
        while True:
            clear_screen()
            header("ALAKH DA DHAABA", "🍽️")
            print(f"{C.GREY}{'FOOD COURT MANAGEMENT SYSTEM'.center(get_width())}{C.RESET}")
            print()
            
            menu_box([
                ("1", "🔐 User Login"),
                ("2", "📝 Create Account"),
                ("3", "👑 Admin Login"),
                ("4", "🚪 Exit"),
            ])
            
            choice = input(f"\n{C.CYAN}Enter your choice: {C.RESET}").strip()
            
            if choice == "1":
                self.login_screen()
            elif choice == "2":
                self.register_screen()
            elif choice == "3":
                self.admin_screen()
            elif choice == "4":
                print()
                success("Thank you for visiting Alakh Da Dhaaba!")
                print(f"{C.CYAN}👋 See you again!{C.RESET}")
                sys.exit(0)
            else:
                error("Please choose a valid option.")
                pause()
    
    def login_screen(self):
        """Login screen"""
        clear_screen()
        header("LOGIN", "🔐")
        print()
        
        username = input(f"{C.CYAN}Username: {C.RESET}").strip()
        password = input(f"{C.CYAN}Password: {C.RESET}").strip()
        
        success_flag, message = self.service.login_user(username, password)
        
        if success_flag:
            success(message)
            pause()
            self.user_portal()
        else:
            error(message)
            pause()
    
    def register_screen(self):
        """Register screen"""
        clear_screen()
        header("CREATE ACCOUNT", "📝")
        print()
        
        username = input(f"{C.CYAN}Choose username: {C.RESET}").strip()
        name = input(f"{C.CYAN}Your name: {C.RESET}").strip()
        password = input(f"{C.CYAN}Create password: {C.RESET}").strip()
        
        success_flag, message = self.service.register_user(username, name, password)
        
        if success_flag:
            success(message)
        else:
            error(message)
        pause()
    
    def browse_food(self):
        """Browse food"""
        all_food = []
        for restaurant_name, restaurant_data in self.service.db.data["restaurants"].items():
            for item_num, item in restaurant_data["menu"].items():
                all_food.append((restaurant_name, item_num, item))
        page = 0
        while True:
            clear_screen()
            header("ALL FOOD", "🍔")
            visible, total_pages = pagination(all_food, page)
            start_number = page * 10
            for offset, (restaurant_name, item_num, item) in enumerate(visible):
                status = "SOLD OUT" if item["stock"] <= 0 else f"{item['stock']} left"
                food_card(str(start_number + offset + 1), item["name"], money(item["price"]), restaurant_name, f"{status}  |  ⭐ {item['rating']}")
            pagination_footer(page, total_pages, len(all_food))
            choice = input(f"{C.CYAN}Food number, n/p, or 0: {C.RESET}").strip().lower()
            if choice == "0":
                return
            if choice == "n" and page < total_pages - 1:
                page += 1
                continue
            if choice == "p" and page > 0:
                page -= 1
                continue
            try:
                index = int(choice) - 1
                restaurant_name, item_num, _ = all_food[index]
                success_flag, message = self.service.add_to_cart(restaurant_name, item_num)
                success(message) if success_flag else error(message)
            except (ValueError, IndexError):
                error("Choose a visible food number or n/p.")
            pause()
    
    def restaurants_screen(self):
        """Restaurants screen"""
        while True:
            clear_screen()
            header("RESTAURANTS", "🏪")
            print()
            
            restaurants = self.service.get_restaurants()
            for index, (name, restaurant) in enumerate(restaurants, 1):
                restaurant_card(
                    index, name, restaurant.emoji, restaurant.cuisine,
                    restaurant.opening_hours, restaurant.service_style,
                    f"{restaurant.available_seats}/{restaurant.total_seats}",
                    restaurant.description,
                )
            
            print(f"\n{C.GREY}0. Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Enter restaurant number: {C.RESET}").strip()
            
            if choice == "0":
                return
            
            try:
                index = int(choice) - 1
                restaurant_name, restaurant = restaurants[index]
                self.show_restaurant_menu(restaurant_name, restaurant)
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
    
    def show_restaurant_menu(self, restaurant_name, restaurant):
        """Show restaurant menu"""
        page = 0
        while True:
            clear_screen()
            header(restaurant_name.upper(), restaurant.emoji)
            print()
            
            menu_items = list(restaurant.menu.items())
            visible, total_pages = pagination(menu_items, page)
            for num, item in visible:
                status = "SOLD OUT" if item.stock <= 0 else f"{item.stock} left"
                food_card(num, item.name, money(item.price), item.category, f"{status}  |  ⭐ {item.rating}")
            
            pagination_footer(page, total_pages, len(menu_items))
            choice = input(f"{C.CYAN}Dish number, n/p, or 0: {C.RESET}").strip().lower()
            
            if choice == "0":
                return
            if choice == "n" and page < total_pages - 1:
                page += 1
                continue
            if choice == "p" and page > 0:
                page -= 1
                continue
            
            success_flag, message = self.service.add_to_cart(restaurant_name, choice)
            if success_flag:
                success(message)
            else:
                error(message)
            pause()
    
    def cart_screen(self):
        """Cart screen"""
        while True:
            clear_screen()
            header("YOUR CART", "🛒")
            print()
            
            if not self.service.cart.items:
                print(f"{C.GREY}Your cart is empty.{C.RESET}")
                pause()
                return
            
            for index, item in enumerate(self.service.cart.items, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {item.name}")
                print(f"   {C.GREY}{item.restaurant} | {money(item.price)} × {item.quantity} = {money(item.total)}{C.RESET}")
                small_line()
            
            print(f"{C.BOLD}💰 Total: {money(self.service.cart.total)}{C.RESET}")
            print()
            
            menu_box([
                ("1", "💳 Checkout"),
                ("2", "➖ Remove Item"),
                ("3", "🔢 Change Quantity"),
                ("4", "🧹 Clear Cart"),
                ("5", "🔙 Back"),
            ])
            
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            
            if choice == "1":
                self.checkout_screen()
                if not self.service.cart.items:
                    return
            elif choice == "2":
                try:
                    index = int(input(f"{C.CYAN}Enter item number to remove: {C.RESET}")) - 1
                    if self.service.cart.remove_item(index):
                        success("Item removed.")
                    else:
                        error("Invalid item number.")
                except ValueError:
                    error("Please enter a number.")
                pause()
            elif choice == "3":
                try:
                    index = int(input(f"{C.CYAN}Enter item number: {C.RESET}")) - 1
                    quantity = int(input(f"{C.CYAN}Enter new quantity: {C.RESET}"))
                    if self.service.cart.update_quantity(index, quantity):
                        success("Quantity updated.")
                    else:
                        error("Invalid quantity.")
                except ValueError:
                    error("Please enter valid numbers.")
                pause()
            elif choice == "4":
                self.service.cart.clear()
                success("Cart cleared.")
                pause()
                return
            elif choice == "5":
                return
            else:
                error("Invalid choice.")
                pause()
    
    def checkout_screen(self):
        """Checkout screen"""
        clear_screen()
        header("CHECKOUT", "💳")
        print()
        
        total = self.service.cart.total
        print(f"Total Amount: {money(total)}")
        
        coupon_code = input(f"{C.CYAN}Coupon code (or press Enter to skip): {C.RESET}").strip()
        
        success_flag, message, order = self.service.place_order(coupon_code)
        
        if success_flag:
            success(message)
            if order:
                print(f"🧾 Order ID: {C.BOLD}{order.id}{C.RESET}")
                print(f"💰 Total Paid: {money(order.total)}")
                print(f"📄 Receipt saved in receipts/ folder")
        else:
            error(message)
        
        pause()
    
    def book_seats_screen(self):
        """Book seats screen"""
        clear_screen()
        header("BOOK SEATS", "🪑")
        print()
        
        restaurants = self.service.get_restaurants()
        for index, (name, restaurant) in enumerate(restaurants, 1):
            print(f"{C.YELLOW}{index}.{C.RESET} {restaurant.emoji} {name} - {seat_bar(restaurant.available_seats, restaurant.total_seats)}")
        
        try:
            choice = int(input(f"\n{C.CYAN}Choose restaurant: {C.RESET}")) - 1
            restaurant_name, restaurant = restaurants[choice]
            
            seats = int(input(f"{C.CYAN}How many seats? {C.RESET}"))
            
            success_flag, message = self.service.book_seats(restaurant_name, seats)
            if success_flag:
                success(message)
            else:
                error(message)
        except (ValueError, IndexError):
            error("Invalid input.")
        
        pause()
    
    def my_reservations_screen(self):
        """My reservations screen"""
        clear_screen()
        header("MY RESERVATIONS", "📅")
        print()
        
        user = self.service.current_user
        if not user:
            return
        
        reservations = [r for r in self.service.db.data.get("reservations", []) 
                       if r["username"] == user.username]
        
        if not reservations:
            print(f"{C.GREY}No reservations found.{C.RESET}")
        else:
            for reservation in reversed(reservations):
                print(f"🧾 {C.BOLD}{reservation['id']}{C.RESET}")
                print(f"🏪 {reservation['restaurant']}")
                print(f"🪑 Seats: {reservation['seats']}")
                print(f"📅 {reservation['date']}")
                print(f"Status: {status_badge(reservation['status'])}")
                small_line()
        
        pause()
    
    def my_orders_screen(self):
        """My orders screen"""
        clear_screen()
        header("MY ORDERS", "📦")
        print()
        
        user = self.service.current_user
        if not user:
            return
        
        orders = [o for o in self.service.db.data.get("orders", []) 
                 if o["username"] == user.username]
        
        if not orders:
            print(f"{C.GREY}No orders found.{C.RESET}")
        else:
            for order in reversed(orders):
                print(f"🧾 {C.BOLD}{order['id']}{C.RESET} | {order['date']}")
                print(f"Status: {status_badge(order['status'])}")
                print(f"Total: {money(order['total'])}")
                for item in order["items"]:
                    print(f"  {C.GREY}•{C.RESET} {item['name']} × {item['quantity']}")
                small_line()
        
        pause()
    
    def favorites_screen(self):
        """Favorites screen"""
        page = 0
        while True:
            clear_screen()
            header("FAVORITES", "❤️")
            print()

            user = self.service.current_user
            if not user:
                return

            if not user.favorites:
                print(f"{C.GREY}No favorites yet.{C.RESET}")
            else:
                visible, total_pages = pagination(user.favorites, page)
                for offset, favorite in enumerate(visible):
                    food_card(
                        str(page * 10 + offset + 1), favorite["name"], money(favorite["price"]),
                        favorite.get("restaurant", "Unknown restaurant"), "Saved favourite",
                    )
                pagination_footer(page, total_pages, len(user.favorites))

            menu_box([
                ("1", "❤️ Add Favorite"),
                ("2", "🗑️ Remove Favorite"),
                ("3", "🔙 Back"),
            ])
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

            if choice == "1":
                self.add_favorite_screen()
            elif choice == "2":
                self.remove_favorite_screen()
            elif choice == "3":
                return
            elif choice.lower() == "n" and user.favorites:
                page = min(page + 1, max((len(user.favorites) - 1) // 10, 0))
            elif choice.lower() == "p" and user.favorites:
                page = max(page - 1, 0)
            else:
                error("Invalid choice.")
                pause()

    def add_favorite_screen(self):
        """Choose a menu item to save as a favorite"""
        clear_screen()
        header("ADD FAVORITE", "❤️")
        print()

        all_food = []
        for restaurant_name, restaurant in self.service.get_restaurants():
            for item_number, item in restaurant.menu.items():
                all_food.append((restaurant_name, item_number, item))

        page = 0
        while True:
            clear_screen()
            header("ADD FAVORITE", "❤️")
            visible, total_pages = pagination(all_food, page)
            for offset, (restaurant_name, _, item) in enumerate(visible):
                food_card(str(page * 10 + offset + 1), item.name, money(item.price), restaurant_name, f"⭐ {item.rating}")
            pagination_footer(page, total_pages, len(all_food))
            choice = input(f"{C.CYAN}Food number, n/p, or 0 cancel: {C.RESET}").strip().lower()
            if choice == "0":
                return
            if choice == "n" and page < total_pages - 1:
                page += 1
                continue
            if choice == "p" and page > 0:
                page -= 1
                continue
            try:
                restaurant_name, item_number, _ = all_food[int(choice) - 1]
                success_flag, message = self.service.add_favorite(restaurant_name, item_number)
                success(message) if success_flag else error(message)
            except (ValueError, IndexError):
                error("Choose a visible food number or n/p.")
            pause()

    def remove_favorite_screen(self):
        """Remove one saved favorite"""
        user = self.service.current_user
        if not user or not user.favorites:
            warn("No favorites to remove.")
            pause()
            return

        try:
            choice = int(input(f"{C.CYAN}Enter favorite number (0 to cancel): {C.RESET}"))
            if choice == 0:
                return
            success_flag, message = self.service.remove_favorite(choice - 1)
            success(message) if success_flag else error(message)
        except ValueError:
            error("Please enter a number.")
        pause()
    
    def wallet_screen(self):
        """Wallet screen"""
        clear_screen()
        header("WALLET", "💰")
        print()
        
        user = self.service.current_user
        if not user:
            return
        
        print(f"Current Balance: {money(user.wallet)}")
        print(f"⭐ Food Points: {C.YELLOW}{user.food_points}{C.RESET}")
        
        try:
            amount = int(input(f"\n{C.CYAN}Enter amount to add (0 to skip): {C.RESET}"))
            if amount > 0:
                success_flag, message = self.service.add_wallet_money(amount)
                success(message) if success_flag else error(message)
            elif amount < 0:
                error("Amount must be greater than zero.")
        except ValueError:
            error("Invalid amount.")
        
        pause()
    
    def reviews_screen(self):
        """Reviews screen"""
        while True:
            clear_screen()
            header("REVIEWS", "⭐")
            print()
            
            menu_box([
                ("1", "⭐ Give a Review"),
                ("2", "👀 View My Reviews"),
                ("3", "🔙 Back"),
            ])
            
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            
            if choice == "1":
                restaurants = self.service.get_restaurants()
                for index, (name, restaurant) in enumerate(restaurants, 1):
                    print(f"{C.YELLOW}{index}.{C.RESET} {restaurant.emoji} {name}")
                
                try:
                    restaurant_choice = int(input(f"\n{C.CYAN}Choose restaurant: {C.RESET}")) - 1
                    restaurant_name = restaurants[restaurant_choice][0]
                    
                    rating = int(input(f"{C.CYAN}Rating (1-5): {C.RESET}"))
                    comment = input(f"{C.CYAN}Write your review: {C.RESET}").strip()
                    
                    success_flag, message = self.service.add_review(restaurant_name, rating, comment)
                    if success_flag:
                        success(message)
                    else:
                        error(message)
                except (ValueError, IndexError):
                    error("Invalid input.")
                
                pause()
            
            elif choice == "2":
                user = self.service.current_user
                if user:
                    if not user.reviews:
                        print(f"{C.GREY}No reviews yet.{C.RESET}")
                    else:
                        for review in user.reviews:
                            stars = "★" * review["rating"] + "☆" * (5 - review["rating"])
                            print(f"\n🏪 {C.BOLD}{review['restaurant']}{C.RESET}")
                            print(f"{C.YELLOW}{stars}{C.RESET} ({review['rating']}/5)")
                            print(f"💬 {review['comment']}")
                            small_line()
                pause()
            
            elif choice == "3":
                return
    
    def notifications_screen(self):
        """Notifications screen"""
        clear_screen()
        header("ANNOUNCEMENTS", "🔔")
        print()
        
        announcements = self.service.db.data.get("announcements", [])
        if not announcements:
            panel("📭  INBOX CLEAR", ["No new announcements right now."], C.GREY)
        else:
            for index, announcement in enumerate(announcements, 1):
                message = announcement if isinstance(announcement, str) else announcement.get("message", "")
                announcement_card(index, message)
        
        pause()
    
    def profile_screen(self):
        """Profile screen"""
        clear_screen()
        header("PROFILE", "👤")
        user = self.service.current_user
        if not user:
            return

        panel("👤  ACCOUNT", [
            f"Name       {C.BOLD}{user.name}{C.RESET}",
            f"Username   {C.CYAN}@{user.username}{C.RESET}",
            f"Joined     {C.GREY}{user.created_at or 'Recently'}{C.RESET}",
        ], C.CYAN)
        panel("💳  BALANCE", [
            f"Wallet     {money(user.wallet)}",
            f"Points     {C.YELLOW}{user.food_points} ⭐{C.RESET}",
        ], C.GREEN)
        panel("📈  ACTIVITY", [
            f"Orders     {C.WHITE}{len(user.orders)}{C.RESET}",
            f"Reserved   {C.WHITE}{len(user.reservations)} seats bookings{C.RESET}",
            f"Favorites  {C.WHITE}{len(user.favorites)} saved items{C.RESET}",
            f"Reviews    {C.WHITE}{len(user.reviews)} submitted{C.RESET}",
        ], C.MAGENTA)
        pause()
    
    def admin_screen(self):
        """Admin login screen"""
        clear_screen()
        header("ADMIN LOGIN", "👑")
        print()
        
        username = input(f"{C.CYAN}Admin username: {C.RESET}").strip()
        password = input(f"{C.CYAN}Admin password: {C.RESET}").strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            success("Admin login successful!")
            pause()
            self.admin_portal()
        else:
            error("Invalid admin credentials.")
            pause()

    def admin_users_screen(self):
        """Manage user accounts"""
        while True:
            clear_screen()
            header("MANAGE USERS", "👥")
            print()
            users = list(self.service.db.data.get("users", {}).items())
            if not users:
                print(f"{C.GREY}No users found.{C.RESET}")
            for index, (username, user_data) in enumerate(users, 1):
                print(
                    f"{C.YELLOW}{index}.{C.RESET} {C.BOLD}{username}{C.RESET} | "
                    f"{user_data.get('name', '')} | Wallet: {money(user_data.get('wallet', 0))} | "
                    f"Points: {user_data.get('food_points', 0)}"
                )
            print(f"\n{C.GREY}0. Back{C.RESET}")
            choice = input(f"{C.CYAN}Choose user to manage: {C.RESET}").strip()
            if choice == "0":
                return
            try:
                username, user_data = users[int(choice) - 1]
            except (ValueError, IndexError):
                error("Invalid user choice.")
                pause()
                continue

            menu_box([("1", "✏️ Edit Profile"), ("2", "💳 Adjust Wallet"), ("3", "🗑️ Delete User"), ("4", "🔙 Back")])
            action = input(f"{C.CYAN}Choose action: {C.RESET}").strip()
            if action == "1":
                print(f"\n{C.GREY}Edit account details. Press Enter to keep the current value.{C.RESET}")
                name = input(f"Name [{user_data.get('name', '')}]: ").strip() or user_data.get("name", "")
                try:
                    points = int(input(f"Food points [{user_data.get('food_points', 0)}]: ").strip() or user_data.get("food_points", 0))
                    wallet = user_data.get("wallet", 0)
                    success_flag, message = self.service.update_user(username, name, wallet, points)
                    success(message) if success_flag else error(message)
                    if success_flag:
                        print(f"{C.GREY}Saved profile for {username}. Wallet remains {money(wallet)}.{C.RESET}")
                except ValueError:
                    error("Food points must be a number.")
                pause()
            elif action == "2":
                print(f"\n{C.GREY}Use a positive amount to credit or a negative amount to debit.{C.RESET}")
                try:
                    amount = int(input(f"Wallet adjustment (+/-): ").strip())
                    reason = input("Reason: ").strip()
                    success_flag, message = self.service.adjust_user_wallet(username, amount, reason)
                    success(message) if success_flag else error(message)
                except ValueError:
                    error("Wallet adjustment must be a number.")
                pause()
            elif action == "3":
                confirm = input(f"Type DELETE to remove {username}: ").strip()
                if confirm == "DELETE":
                    success_flag, message = self.service.delete_user(username)
                    success(message) if success_flag else error(message)
                else:
                    warn("Deletion cancelled.")
                pause()

    def admin_orders_screen(self):
        """View order details and update order status"""
        while True:
            clear_screen()
            header("MANAGE ORDERS", "📦")
            print()
            orders = self.service.db.data.get("orders", [])
            if not orders:
                print(f"{C.GREY}No orders found.{C.RESET}")
                pause()
                return
            for index, order in enumerate(reversed(orders), 1):
                print(
                    f"{C.YELLOW}{index}.{C.RESET} {order.get('id', 'N/A')} | "
                    f"{order.get('username', 'unknown')} | {money(order.get('total', 0))} | "
                    f"{status_badge(order.get('status', 'Unknown'))}"
                )
            print(f"\n{C.GREY}0. Back{C.RESET}")
            choice = input(f"{C.CYAN}Choose order: {C.RESET}").strip()
            if choice == "0":
                return
            try:
                order = list(reversed(orders))[int(choice) - 1]
            except (ValueError, IndexError):
                error("Invalid order choice.")
                pause()
                continue

            clear_screen()
            header(f"ORDER {order.get('id', 'N/A')}", "📦")
            print(f"Customer: {order.get('username', 'unknown')}   Date: {order.get('date', 'N/A')}")
            print(f"Status: {status_badge(order.get('status', 'Unknown'))}\n")
            for item_index, item in enumerate(order.get("items", []), 1):
                quantity = item.get("quantity", 0)
                print(f"{C.YELLOW}{item_index}.{C.RESET} {item.get('name', 'Unknown item')} × {quantity} = {money(item.get('price', 0) * quantity)}")
            print(f"\nTotal: {money(order.get('total', 0))}")
            if order.get("status") in {"Delivered", "Cancelled"}:
                print(f"{C.GREY}🔒 This order is closed and its items cannot be edited.{C.RESET}")
                pause()
                continue

            print("\n1. Edit item quantity")
            print("2. Update order status")
            print("0. Back")
            action = input(f"{C.CYAN}Choose action: {C.RESET}").strip()
            if action == "0":
                continue
            if action == "1":
                try:
                    item_choice = int(input(f"{C.CYAN}Item number to edit: {C.RESET}")) - 1
                    quantity = int(input(f"{C.CYAN}New quantity: {C.RESET}"))
                    success_flag, message = self.service.update_order_item_quantity(order["id"], item_choice, quantity)
                    success(message) if success_flag else error(message)
                except ValueError:
                    error("Item number and quantity must be numbers.")
                pause()
                continue
            if action != "2":
                error("Invalid action.")
                pause()
                continue

            statuses = ["Preparing", "Confirmed", "Ready", "Delivered", "Cancelled"]
            for status_index, status in enumerate(statuses, 1):
                print(f"{status_index}. {status_badge(status)}")
            print("0. Back")
            try:
                status_choice = int(input(f"{C.CYAN}Choose new status: {C.RESET}"))
                if status_choice == 0:
                    continue
                success_flag, message = self.service.update_order_status(order["id"], statuses[status_choice - 1])
                success(message) if success_flag else error(message)
            except (ValueError, IndexError):
                error("Invalid status choice.")
            pause()

    def admin_reviews_screen(self):
        """Review and delete submitted reviews"""
        while True:
            clear_screen()
            header("MANAGE REVIEWS", "⭐")
            print()
            reviews = self.service.db.data.get("reviews", [])
            if not reviews:
                print(f"{C.GREY}No reviews found.{C.RESET}")
            for index, review in enumerate(reviews, 1):
                stars = "★" * int(review.get("rating", 0)) + "☆" * (5 - int(review.get("rating", 0)))
                print(f"{C.YELLOW}{index}.{C.RESET} {review.get('restaurant', 'Unknown')} | {review.get('username', 'unknown')} | {C.YELLOW}{stars}{C.RESET}")
                print(f"   {review.get('comment', '')}")
            print(f"\n{C.GREY}0. Back{C.RESET}")
            choice = input(f"{C.CYAN}Review number to delete: {C.RESET}").strip()
            if choice == "0":
                return
            try:
                success_flag, message = self.service.delete_review(int(choice) - 1)
                success(message) if success_flag else error(message)
            except ValueError:
                error("Please enter a number.")
            pause()

    def admin_restaurants_screen(self):
        """Manage hotel-style restaurant branches and their menus"""
        while True:
            clear_screen()
            header("MANAGE HOTELS / RESTAURANTS", "🏪")
            print()
            restaurants = list(self.service.db.data.get("restaurants", {}).items())
            for index, (name, restaurant) in enumerate(restaurants, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {restaurant.get('emoji', '🍽️')} {name} | Seats: {restaurant.get('available_seats', 0)}/{restaurant.get('total_seats', 0)} | Foods: {len(restaurant.get('menu', {}))}")
            menu_box([("1", "➕ Add Hotel / Restaurant"), ("2", "🛠️ Manage Branch"), ("3", "🗑️ Remove Branch"), ("4", "🔙 Back")])
            action = input(f"{C.CYAN}Choose: {C.RESET}").strip()
            if action == "1":
                name = input("Restaurant name: ").strip()
                emoji = input("Emoji (optional): ").strip()
                try:
                    seats = int(input("Total seats: ").strip())
                    success_flag, message = self.service.add_restaurant(name, emoji, seats)
                    success(message) if success_flag else error(message)
                except ValueError:
                    error("Seats must be a number.")
                pause()
            elif action in {"2", "3"}:
                if not restaurants:
                    error("No restaurants available.")
                    pause()
                    continue
                try:
                    index = int(input("Restaurant number: ").strip()) - 1
                    name = restaurants[index][0]
                except (ValueError, IndexError):
                    error("Invalid restaurant choice.")
                    pause()
                    continue
                if action == "3":
                    confirm = input(f"Type DELETE to remove {name}: ").strip()
                    if confirm == "DELETE":
                        success_flag, message = self.service.remove_restaurant(name)
                        success(message) if success_flag else error(message)
                    else:
                        warn("Removal cancelled.")
                    pause()
                else:
                    self.admin_branch_screen(name)
            elif action == "4":
                return

    def admin_branch_screen(self, restaurant_name):
        """Manage one restaurant's food menu"""
        while True:
            restaurant = self.service.db.data["restaurants"].get(restaurant_name)
            if not restaurant:
                return
            clear_screen()
            header(restaurant_name.upper(), restaurant.get("emoji", "🍽️"))
            print()
            for number, item in restaurant.get("menu", {}).items():
                print(f"{number}. {item.get('name', 'Unknown')} | {money(item.get('price', 0))} | Stock: {item.get('stock', 0)}")
            menu_box([("1", "➕ Add Food"), ("2", "🗑️ Remove Food"), ("3", "🪑 Manage Seats"), ("4", "🔙 Back")])
            action = input(f"{C.CYAN}Choose: {C.RESET}").strip()
            if action == "1":
                try:
                    item = {
                        "name": input("Food name: ").strip(),
                        "price": int(input("Price: ").strip()),
                        "category": input("Category: ").strip() or "General",
                        "description": input("Description: ").strip(),
                        "stock": int(input("Stock: ").strip()),
                        "rating": float(input("Rating (0-5): ").strip() or "0"),
                    }
                    if not 0 <= item["rating"] <= 5:
                        raise ValueError
                    success_flag, message = self.service.add_menu_item(restaurant_name, item)
                    success(message) if success_flag else error(message)
                except ValueError:
                    error("Price, stock, and rating must be valid numbers.")
                pause()
            elif action == "2":
                item_number = input("Food number to remove: ").strip()
                confirm = input("Type DELETE to confirm: ").strip()
                if confirm == "DELETE":
                    success_flag, message = self.service.remove_menu_item(restaurant_name, item_number)
                    success(message) if success_flag else error(message)
                else:
                    warn("Removal cancelled.")
                pause()
            elif action == "3":
                try:
                    available_seats = int(input(f"Available seats (0-{restaurant.get('total_seats', 0)}): ").strip())
                    success_flag, message = self.service.set_available_seats(restaurant_name, available_seats)
                    success(message) if success_flag else error(message)
                except ValueError:
                    error("Available seats must be a number.")
                pause()
            elif action == "4":
                return

    def admin_announcements_screen(self):
        """Publish and remove announcements"""
        while True:
            clear_screen()
            header("ANNOUNCEMENTS", "🔔")
            print()
            announcements = self.service.db.data.get("announcements", [])
            for index, announcement in enumerate(announcements, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} 📢 {announcement if isinstance(announcement, str) else announcement.get('message', '')}")
            menu_box([("1", "📣 Publish Announcement"), ("2", "🗑️ Remove Announcement"), ("3", "🔙 Back")])
            action = input(f"{C.CYAN}Choose: {C.RESET}").strip()
            if action == "1":
                message = input("Announcement: ").strip()
                success_flag, result = self.service.add_announcement(message)
                success(result) if success_flag else error(result)
                pause()
            elif action == "2":
                try:
                    success_flag, result = self.service.remove_announcement(int(input("Announcement number: ").strip()) - 1)
                    success(result) if success_flag else error(result)
                except ValueError:
                    error("Please enter a number.")
                pause()
            elif action == "3":
                return

    def admin_stats_screen(self):
        """Show an interactive dashboard summary"""
        while True:
            clear_screen()
            header("DASHBOARD STATS", "📊")
            print(f"{C.GREY}LIVE OPERATIONS SNAPSHOT  •  Press Enter to refresh{C.RESET}\n")
            stats = self.service.get_revenue_stats()

            metric_cards([
                ("NET REVENUE", money_plain(stats["total_revenue"]), C.GREEN),
                ("ACTIVE ORDERS", str(stats["total_orders"]), C.CYAN),
                ("AVERAGE ORDER", money_plain(stats["avg_order"]), C.YELLOW),
                ("CANCELLED", str(stats["cancelled_orders"]), C.RED),
                ("CUSTOMERS", str(stats["user_count"]), C.MAGENTA),
                ("BRANCHES", str(stats["restaurant_count"]), C.ORANGE),
            ])

            print()
            sub_header("ORDER FLOW", "◈")
            maximum_status_count = max(stats["status_counts"].values(), default=1)
            for status, count in stats["status_counts"].items():
                print(f"{status_badge(status)} {progress_bar(count, maximum_status_count, 18)} {C.WHITE}{count}{C.RESET}")

            print()
            top_items = stats["top_items"]
            maximum_item_quantity = max((quantity for _, quantity in top_items), default=1)
            item_rows = [
                f"{index}. {name[:20]:<20} {progress_bar(quantity, maximum_item_quantity, 12, C.YELLOW)} {quantity} sold"
                for index, (name, quantity) in enumerate(top_items, 1)
            ]
            if not item_rows:
                item_rows = [f"{C.GREY}No completed sales yet.{C.RESET}"]
            panel("TOP FOOD ITEMS", item_rows, C.MAGENTA)

            branch_rows = []
            maximum_branch_revenue = max((revenue for _, revenue in stats["restaurant_revenue"]), default=1)
            for name, revenue in stats["restaurant_revenue"]:
                branch_rows.append(
                    f"{name[:18]:<18} {progress_bar(revenue, maximum_branch_revenue, 14, C.GREEN)} {money_plain(revenue)}"
                )
            if not branch_rows:
                branch_rows = [f"{C.GREY}No branch revenue yet.{C.RESET}"]
            panel("BRANCH PERFORMANCE", branch_rows, C.CYAN)

            print(f"\n{C.DIM}Enter = refresh dashboard    0 = back to admin portal{C.RESET}")
            if input(f"{C.CYAN}Action: {C.RESET}").strip() == "0":
                return

if __name__ == "__main__":
    app = FoodCourtApp()
    app.run()