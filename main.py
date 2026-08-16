"""
Alakh Da Dhaaba - Main Entry Point
"""

from services import FoodCourtService
from ui import *
import sys

class FoodCourtApp:
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
    
    def user_portal(self):
        """User portal"""
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
                ("1", "🍔 Browse Food"),
                ("2", "🏪 Restaurants"),
                ("3", "🛒 Cart"),
                ("4", "🪑 Book Seats"),
                ("5", "📅 My Reservations"),
                ("6", "📦 My Orders"),
                ("7", "❤️ Favorites"),
                ("8", "💰 Wallet"),
                ("9", "⭐ Reviews"),
                ("10", "🔔 Notifications"),
                ("11", "👤 Profile"),
                ("12", "🚪 Logout"),
            ])
            
            choice = input(f"\n{C.CYAN}Enter your choice: {C.RESET}").strip()
            
            if choice == "1":
                self.browse_food()
            elif choice == "2":
                self.restaurants_screen()
            elif choice == "3":
                self.cart_screen()
            elif choice == "4":
                self.book_seats_screen()
            elif choice == "5":
                self.my_reservations_screen()
            elif choice == "6":
                self.my_orders_screen()
            elif choice == "7":
                self.favorites_screen()
            elif choice == "8":
                self.wallet_screen()
            elif choice == "9":
                self.reviews_screen()
            elif choice == "10":
                self.notifications_screen()
            elif choice == "11":
                self.profile_screen()
            elif choice == "12":
                self.service.logout_user()
                success("Logged out successfully!")
                pause()
                return
            else:
                error("Invalid choice.")
                pause()
    
    def browse_food(self):
        """Browse food"""
        clear_screen()
        header("BROWSE FOOD", "🍔")
        print()
        
        all_food = []
        for restaurant_name, restaurant_data in self.service.db.data["restaurants"].items():
            for item_num, item in restaurant_data["menu"].items():
                all_food.append((restaurant_name, item_num, item))
        
        for index, (restaurant_name, item_num, item) in enumerate(all_food, 1):
            status = "SOLD OUT" if item["stock"] <= 0 else f"{item['stock']} left"
            print(f"{C.YELLOW}{index}.{C.RESET} {item['name']} - {money(item['price'])}")
            print(f"   {C.GREY}{restaurant_name} | {status} | ⭐ {item['rating']}{C.RESET}")
        
        choice = input(f"\n{C.CYAN}Enter food number to add to cart (0 to back): {C.RESET}").strip()
        
        if choice == "0":
            return
        
        try:
            index = int(choice) - 1
            restaurant_name, item_num, item = all_food[index]
            success_flag, message = self.service.add_to_cart(restaurant_name, item_num)
            if success_flag:
                success(message)
            else:
                error(message)
        except (ValueError, IndexError):
            error("Invalid choice.")
        
        pause()
    
    def restaurants_screen(self):
        """Restaurants screen"""
        while True:
            clear_screen()
            header("RESTAURANTS", "🏪")
            print()
            
            restaurants = self.service.get_restaurants()
            for index, (name, restaurant) in enumerate(restaurants, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {restaurant.emoji} {C.BOLD}{name}{C.RESET}")
                print(f"     {seat_bar(restaurant.available_seats, restaurant.total_seats)}")
            
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
        while True:
            clear_screen()
            header(restaurant_name.upper(), restaurant.emoji)
            print()
            
            for num, item in restaurant.menu.items():
                status = "SOLD OUT" if item.stock <= 0 else f"{item.stock} left"
                print(f"{C.YELLOW}{num}.{C.RESET} {item.name} - {money(item.price)}")
                print(f"   {C.GREY}{item.description} | {status} | ⭐ {item.rating}{C.RESET}")
            
            print(f"\n{C.GREY}0. Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Enter dish number to add: {C.RESET}").strip()
            
            if choice == "0":
                return
            
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
        clear_screen()
        header("FAVORITES", "❤️")
        print()
        
        user = self.service.current_user
        if not user:
            return
        
        if not user.favorites:
            print(f"{C.GREY}No favorites yet.{C.RESET}")
        else:
            for index, fav in enumerate(user.favorites, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {fav['name']} - {money(fav['price'])}")
        
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
                user.wallet += amount
                self.service.db.data["users"][user.username]["wallet"] = user.wallet
                self.service.db.save()
                success(f"Added {money_plain(amount)} to wallet!")
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
        
        for announcement in self.service.db.data.get("announcements", []):
            print(f"{C.YELLOW}📢{C.RESET} {announcement}")
        
        pause()
    
    def profile_screen(self):
        """Profile screen"""
        clear_screen()
        header("PROFILE", "👤")
        print()
        
        user = self.service.current_user
        if not user:
            return
        
        print(f"Name: {C.BOLD}{user.name}{C.RESET}")
        print(f"Username: {user.username}")
        print(f"Wallet: {money(user.wallet)}")
        print(f"Food Points: {C.YELLOW}{user.food_points}{C.RESET}")
        print(f"Favorites: {len(user.favorites)}")
        print(f"Orders: {len(user.orders)}")
        print(f"Reviews: {len(user.reviews)}")
        
        pause()
    
    def admin_screen(self):
        """Admin login screen"""
        clear_screen()
        header("ADMIN LOGIN", "👑")
        print()
        
        username = input(f"{C.CYAN}Admin username: {C.RESET}").strip()
        password = input(f"{C.CYAN}Admin password: {C.RESET}").strip()
        
        if username == "admin" and password == "admin123":
            success("Admin login successful!")
            pause()
            self.admin_portal()
        else:
            error("Invalid admin credentials.")
            pause()
    
    def admin_portal(self):
        """Admin portal"""
        while True:
            clear_screen()
            header("ADMIN PORTAL", "👑")
            print()
            
            menu_box([
                ("1", "👥 View Users"),
                ("2", "📦 View Orders"),
                ("3", "💰 Revenue Stats"),
                ("4", "🪑 Manage Seats"),
                ("5", "🔔 Send Announcement"),
                ("6", "💾 Backup Data"),
                ("7", "🚪 Logout"),
            ])
            
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            
            if choice == "1":
                clear_screen()
                header("USERS", "👥")
                print()
                for username, user_data in self.service.db.data["users"].items():
                    print(f"👤 {C.BOLD}{username}{C.RESET} | {user_data['name']} | Wallet: {money(user_data['wallet'])}")
                pause()
            
            elif choice == "2":
                clear_screen()
                header("ORDERS", "📦")
                print()
                for order in self.service.db.data["orders"]:
                    print(f"🧾 {order['id']} | {order['username']} | {money(order['total'])} | {status_badge(order['status'])}")
                pause()
            
            elif choice == "3":
                clear_screen()
                header("REVENUE", "💰")
                print()
                stats = self.service.get_revenue_stats()
                print(f"Total Revenue: {money(stats['total_revenue'])}")
                print(f"Total Orders: {stats['total_orders']}")
                print(f"Average Order: {money(stats['avg_order'])}")
                pause()
            
            elif choice == "4":
                clear_screen()
                header("MANAGE SEATS", "🪑")
                print()
                restaurants = self.service.get_restaurants()
                for index, (name, restaurant) in enumerate(restaurants, 1):
                    print(f"{C.YELLOW}{index}.{C.RESET} {restaurant.emoji} {name} - {seat_bar(restaurant.available_seats, restaurant.total_seats)}")
                
                try:
                    choice_idx = int(input(f"\n{C.CYAN}Choose restaurant to reset: {C.RESET}")) - 1
                    restaurant_name = restaurants[choice_idx][0]
                    self.service.db.data["restaurants"][restaurant_name]["available_seats"] = \
                        self.service.db.data["restaurants"][restaurant_name]["total_seats"]
                    self.service.db.save()
                    success(f"Seats reset for {restaurant_name}!")
                except (ValueError, IndexError):
                    error("Invalid choice.")
                pause()
            
            elif choice == "5":
                clear_screen()
                header("SEND ANNOUNCEMENT", "🔔")
                print()
                message = input(f"{C.CYAN}Enter announcement: {C.RESET}").strip()
                if message:
                    self.service.db.data["announcements"].append(message)
                    self.service.db.save()
                    success("Announcement sent!")
                else:
                    error("Announcement cannot be empty.")
                pause()
            
            elif choice == "6":
                backup_path = self.service.db.backup()
                success(f"Backup created at: {backup_path}")
                pause()
            
            elif choice == "7":
                return

if __name__ == "__main__":
    app = FoodCourtApp()
    app.run()