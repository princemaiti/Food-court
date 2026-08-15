

# ============================================================
# 🍽️  ALAKH DA DHAABA
# Python-only Food Court Management System
# Uses only Python standard library (JSON for permanent storage)
# ============================================================

import hashlib
import json
import os
import shutil
from datetime import datetime

DATA_FILE = "alakh_dhaaba_data.json"


# ============================================================
# DESIGN SYSTEM (ANSI colors + box drawing — stdlib only)
# ============================================================

# Enable ANSI escape codes on Windows terminals.
if os.name == "nt":
    os.system("")
# "If I'm running on Windows, do this terminal setup." meaning if above code is running on windows then it will enable the ANSI escape codes for colors and styles in the terminal.    

# using ANSI cuz linux terminals support ANSI escape codes natively, so this code is mainly for Windows users.
# class is like container of all those ANSI escape codes
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[38;5;203m"
    GREEN = "\033[38;5;114m"
    YELLOW = "\033[38;5;221m"
    BLUE = "\033[38;5;75m"
    CYAN = "\033[38;5;80m"
    MAGENTA = "\033[38;5;176m"
    ORANGE = "\033[38;5;215m"
    GREY = "\033[38;5;244m"
    WHITE = "\033[38;5;255m"


# because of shutil program refuses to make its UI wider than 64 characters.

def _width():
    """Terminal width, capped for readability."""
    try:
        return min(shutil.get_terminal_size().columns, 64)
    except OSError:
        return 64

# clear the screen for better readability of the terminal output.
'''
if os.name == "nt":
    command = "cls"
else:
    command = "clear"

    nt = windows
    os = operating system
'''
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# char * _width() means it will print the character char repeated _width() times, where _width() is the width of the terminal (capped at 64 characters). This creates a horizontal line across the terminal. The line is printed in the specified color, and then the color is reset to default using C.RESET.
# "-" * 60 = --------------- ...
# grey line 60 * "-" time long with c.reset so the color don't leak 
def line(char="─", color=C.GREY):
    print(f"{color}{char * _width()}{C.RESET}")

# Print a small horizontal line in grey.
# ························ = output
def small_line():
    line("·", C.GREY)

# \n = for new line, f = formatted string, C.DIM = dim color, C.RESET = reset color
def pause():
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

# w is the width of the terminal, label is the title of the section, and emoji is an optional emoji to display alongside the title.
# The function prints a box around the title, with a cyan border and white text. The title is centered within the box.
def header(title, emoji=""):
    """Boxed, centered section title."""
    w = _width()
    label = f" {emoji}  {title} " if emoji else f" {title} "
    print(f"{C.CYAN}{'═' * w}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}{label.center(w)}{C.RESET}")
    print(f"{C.CYAN}{'═' * w}{C.RESET}")

# Print a sub-header with a magenta color and a grey underline.
def sub_header(title, emoji=""):
    w = _width()
    label = f"{emoji}  {title}" if emoji else title
    print(f"{C.MAGENTA}{label}{C.RESET}")
    # Make the underline long enough for the title, but never longer than the terminal.
    print(f"{C.GREY}{'─' * min(len(label) + 4, w)}{C.RESET}")


# GREEN_CODE + ₹149 + RESET_CODE

def success(msg):
    print(f"{C.GREEN}✅ {msg}{C.RESET}")


# RED_CODE + ⚠️  + RESET_CODE
def error(msg):
    print(f"{C.RED}❌ {msg}{C.RESET}")

# YELLOW_CODE + ⚠️  + RESET_CODE
def warn(msg):
    print(f"{C.YELLOW}⚠️  {msg}{C.RESET}")

# BLUE_CODE + ℹ️  + RESET_CODE
def info(msg):
    print(f"{C.BLUE}ℹ️  {msg}{C.RESET}")

#GREEN_CODE + ₹149 + RESET_CODE
def money(amount):
    return f"{C.GREEN}₹{amount}{C.RESET}"

# Print money amount without any color codes.
def money_plain(amount):
    """Un-colored version, for embedding inside already-colored strings."""
    return f"₹{amount}"


def menu_box(options):
    """Pretty-print a numbered menu list: [(number, label), ...]."""
    w = _width()
    print(f"{C.CYAN}┌{'─' * (w - 2)}┐{C.RESET}")
    for number, label in options:
        text = f" {C.YELLOW}{number}.{C.RESET} {label}" 
        pad = w - 2 - len(f" {number}. {label}")
        # │ 1. Browse Food          │ <= output 
        print(f"{C.CYAN}│{C.RESET}{text}{' ' * max(pad, 0)}{C.CYAN}│{C.RESET}")
    print(f"{C.CYAN}└{'─' * (w - 2)}┘{C.RESET}")

# this function takes a status string as input and returns a colored badge for that status. The colors are defined in a dictionary,
# and the function uses ANSI escape codes to format the output. If the status is not found in the dictionary, it defaults to white color.
def status_badge(status):
    colors = {
        "Preparing": C.YELLOW,
        "Confirmed": C.GREEN,
        "Ready": C.CYAN,
        "Delivered": C.GREEN,
        "Cancelled": C.RED,
    }
    color = colors.get(status, C.WHITE)
    return f"{color}{C.BOLD}{status}{C.RESET}"

# all below is just calculation nothing complex, it just calculates the available seats and total seats and 
# then creates a visual bar representation of the seat occupancy using filled and empty blocks. 
# The filled blocks are represented by '█' and the empty blocks by '░'. The function returns a string that includes the visual bar along with the available and total seat counts.

def seat_bar(available, total, width=20):
    """Small visual bar showing seat occupancy."""
    if total <= 0:
        return ""
    filled = round((available / total) * width)
    filled = max(0, min(width, filled))
    bar = f"{C.GREEN}{'█' * filled}{C.GREY}{'░' * (width - filled)}{C.RESET}"
    return f"{bar} {C.WHITE}{available}/{total}{C.RESET}"


# ============================================================
# DATA
# ============================================================

DEFAULT_DATA = {
    "users": {
        "prince": {
            "password": "2007",
            "name": "Prince",
            "wallet": 1000,
            "food_points": 0,
            "favorites": [],
            "reservations": [],
            "orders": [],
            "reviews": []
        },
        "winkle": {
            "password": "2711",
            "name": "Winkle",
            "wallet": 1000,
            "food_points": 0,
            "favorites": [],
            "reservations": [],
            "orders": [],
            "reviews": []
        }
    },

    "activity_logs": [],
    "coupons": [
        {"code": "SAVE10", "type": "percent", "value": 10, "description": "10% off order"},
        {"code": "FLAT50", "type": "flat", "value": 50, "description": "₹50 off order"}
    ],

"restaurants": {
    "Pizza Palace": {
        "emoji": "🍕",
        "total_seats": 20,
        "available_seats": 20,
        "menu": {
            "1": {"name": "Margherita Pizza", "price": 149},
            "2": {"name": "Farmhouse Pizza", "price": 199},
            "3": {"name": "Paneer Tikka Pizza", "price": 229},
            "4": {"name": "Veggie Supreme Pizza", "price": 219},
            "5": {"name": "Cheese Burst Pizza", "price": 249},
            "6": {"name": "Mexican Green Wave Pizza", "price": 229},
            "7": {"name": "Corn & Cheese Pizza", "price": 189},
            "8": {"name": "Spicy Paneer Pizza", "price": 239},
            "9": {"name": "Mushroom & Olive Pizza", "price": 219},
            "10": {"name": "Peri Peri Veg Pizza", "price": 229},
            "11": {"name": "Cheese Overload Pizza", "price": 269},
            "12": {"name": "Tandoori Paneer Pizza", "price": 249},
            "13": {"name": "Garlic Cheese Bread", "price": 119},
            "14": {"name": "Cheesy Garlic Bread", "price": 149},
            "15": {"name": "Stuffed Garlic Bread", "price": 169},
            "16": {"name": "French Fries", "price": 89},
            "17": {"name": "Peri Peri Fries", "price": 109},
            "18": {"name": "Cheese Fries", "price": 129},
            "19": {"name": "Veg Pizza Pocket", "price": 139},
            "20": {"name": "Chocolate Lava Cake", "price": 119},
            "21": {"name": "Brownie with Ice Cream", "price": 149},
            "22": {"name": "Cold Coffee", "price": 99},
            "23": {"name": "Chocolate Shake", "price": 129},
            "24": {"name": "Strawberry Shake", "price": 129}
        }
    },

    "Wok Express": {
        "emoji": "🍜",
        "total_seats": 15,
        "available_seats": 15,
        "menu": {
            "1": {"name": "Veg Hakka Noodles", "price": 129},
            "2": {"name": "Schezwan Fried Rice", "price": 139},
            "3": {"name": "Chilli Paneer", "price": 169},
            "4": {"name": "Veg Fried Rice", "price": 119},
            "5": {"name": "Schezwan Noodles", "price": 139},
            "6": {"name": "Singapore Noodles", "price": 149},
            "7": {"name": "Manchurian Noodles", "price": 149},
            "8": {"name": "Chilli Garlic Noodles", "price": 139},
            "9": {"name": "Paneer Fried Rice", "price": 159},
            "10": {"name": "Burnt Garlic Fried Rice", "price": 149},
            "11": {"name": "Veg Manchurian", "price": 139},
            "12": {"name": "Chilli Mushroom", "price": 159},
            "13": {"name": "Honey Chilli Potato", "price": 149},
            "14": {"name": "Crispy Corn", "price": 139},
            "15": {"name": "Spring Rolls", "price": 109},
            "16": {"name": "Veg Momos", "price": 99},
            "17": {"name": "Fried Momos", "price": 119},
            "18": {"name": "Schezwan Momos", "price": 129},
            "19": {"name": "Chilli Garlic Paneer", "price": 179},
            "20": {"name": "Hot & Sour Soup", "price": 89},
            "21": {"name": "Manchow Soup", "price": 99},
            "22": {"name": "Sweet Corn Soup", "price": 89},
            "23": {"name": "Chinese Bhel", "price": 119},
            "24": {"name": "Veg Spring Roll Platter", "price": 159}
        }
    },

    "Spice Hub": {
        "emoji": "🍚",
        "total_seats": 25,
        "available_seats": 25,
        "menu": {
            "1": {"name": "Paneer Butter Masala", "price": 179},
            "2": {"name": "Veg Biryani", "price": 159},
            "3": {"name": "Masala Dosa", "price": 99},
            "4": {"name": "Shahi Paneer", "price": 189},
            "5": {"name": "Kadai Paneer", "price": 179},
            "6": {"name": "Palak Paneer", "price": 169},
            "7": {"name": "Paneer Tikka Masala", "price": 189},
            "8": {"name": "Dal Makhani", "price": 139},
            "9": {"name": "Dal Tadka", "price": 119},
            "10": {"name": "Chole Masala", "price": 129},
            "11": {"name": "Mix Veg Curry", "price": 149},
            "12": {"name": "Jeera Rice", "price": 99},
            "13": {"name": "Veg Pulao", "price": 119},
            "14": {"name": "Paneer Biryani", "price": 179},
            "15": {"name": "Butter Naan", "price": 49},
            "16": {"name": "Garlic Naan", "price": 69},
            "17": {"name": "Cheese Naan", "price": 99},
            "18": {"name": "Tandoori Roti", "price": 29},
            "19": {"name": "Plain Roti", "price": 25},
            "20": {"name": "Veg Thali", "price": 199},
            "21": {"name": "Paneer Thali", "price": 229},
            "22": {"name": "Samosa", "price": 25},
            "23": {"name": "Paneer Pakora", "price": 119},
            "24": {"name": "Gulab Jamun", "price": 69},
            "25": {"name": "Rasmalai", "price": 89}
        }
    },

    "Burger Point": {
        "emoji": "🍔",
        "total_seats": 10,
        "available_seats": 10,
        "menu": {
            "1": {"name": "Classic Veg Burger", "price": 99},
            "2": {"name": "Paneer Crunch Burger", "price": 139},
            "3": {"name": "Double Cheese Burger", "price": 159},
            "4": {"name": "Aloo Tikki Burger", "price": 79},
            "5": {"name": "Spicy Veg Burger", "price": 109},
            "6": {"name": "Mexican Burger", "price": 139},
            "7": {"name": "Peri Peri Paneer Burger", "price": 149},
            "8": {"name": "Cheese Blast Burger", "price": 169},
            "9": {"name": "Mushroom Burger", "price": 139},
            "10": {"name": "Corn & Cheese Burger", "price": 129},
            "11": {"name": "Paneer Tandoori Burger", "price": 159},
            "12": {"name": "Jumbo Veg Burger", "price": 179},
            "13": {"name": "Classic French Fries", "price": 89},
            "14": {"name": "Peri Peri Fries", "price": 109},
            "15": {"name": "Cheese Fries", "price": 129},
            "16": {"name": "Loaded Nachos", "price": 149},
            "17": {"name": "Cheese Nachos", "price": 129},
            "18": {"name": "Veg Nuggets", "price": 109},
            "19": {"name": "Cheese Balls", "price": 119},
            "20": {"name": "Onion Rings", "price": 99},
            "21": {"name": "Chocolate Shake", "price": 129},
            "22": {"name": "Oreo Shake", "price": 139},
            "23": {"name": "Cold Coffee", "price": 99},
            "24": {"name": "Vanilla Shake", "price": 119}
        }
    }

},

    "orders": [],
    "reviews": [],
    "announcements": [
        "🎉 Welcome to Alakh Da Dhaaba!",
        "🔥 Get delicious food from our best restaurants."
    ],
    "next_order_id": 1001,
    "next_reservation_id": 501
}


# ============================================================
# BASIC HELPERS
# ============================================================

def sync_restaurant_menus(data):
    """Refresh stale restaurant menus from the latest default menu data."""
    restaurants = data.setdefault("restaurants", {})
    updated = False

    for restaurant_name, default_restaurant in DEFAULT_DATA["restaurants"].items():
        current_restaurant = restaurants.get(restaurant_name)

        if not isinstance(current_restaurant, dict):
            restaurants[restaurant_name] = default_restaurant
            updated = True
            continue

        default_menu = default_restaurant.get("menu", {})
        current_menu = current_restaurant.get("menu", {})

        if not isinstance(current_menu, dict) or len(current_menu) < len(default_menu):
            current_restaurant["menu"] = default_menu
            updated = True

    return updated


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Add missing keys if an older data file exists.
        for key, value in DEFAULT_DATA.items():
            if key not in data:
                data[key] = value

        if sync_restaurant_menus(data):
            save_data(data)

        if normalize_restaurant_data(data):
            save_data(data)

        if apply_realistic_food_defaults(data):
            save_data(data)

        for restaurant in data.get("restaurants", {}).values():
            for item in restaurant.get("menu", {}).values():
                if not isinstance(item, dict):
                    continue
                if "rating" not in item or "stock" not in item or "description" not in item or "category" not in item:
                    item.update(normalize_menu_item(item, item.get("name", "Food item")))

        if "activity_logs" not in data:
            data["activity_logs"] = []
        if "coupons" not in data:
            data["coupons"] = DEFAULT_DATA["coupons"]

        return data

    except (json.JSONDecodeError, OSError):
        warn("Data file could not be read. Creating a fresh database.")
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_current_user(data, username):
    return data["users"].get(username)


def generate_order_id(data):
    order_id = data["next_order_id"]
    data["next_order_id"] += 1
    return f"ALD{order_id}"


def generate_reservation_id(data):
    reservation_id = data["next_reservation_id"]
    data["next_reservation_id"] += 1
    return f"RES{reservation_id}"


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, hashed_password):
    if not hashed_password:
        return False

    if hashed_password.startswith("$sha256$"):
        return hashed_password == f"$sha256${hash_password(password)}"

    return hashed_password == password or hashed_password == hash_password(password)


def add_activity_log(data, action, details="", username="system"):
    logs = data.setdefault("activity_logs", [])
    entry = {
        "time": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        "action": action,
        "username": username,
        "details": details
    }
    logs.append(entry)
    if len(logs) > 200:
        logs[:] = logs[-200:]

    try:
        log_path = "log.json"
        existing = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as file:
                try:
                    existing = json.load(file)
                    if not isinstance(existing, list):
                        existing = []
                except json.JSONDecodeError:
                    existing = []
        existing.append(entry)
        if len(existing) > 250:
            existing = existing[-250:]
        with open(log_path, "w", encoding="utf-8") as file:
            json.dump(existing, file, indent=4, ensure_ascii=False)
    except OSError:
        pass


def make_realistic_food_item(name, price, category, description, stock=None):
    if stock is None:
        stock = 8 + (sum(ord(ch) for ch in name) % 18)
    rating = 3.6 + ((sum(ord(ch) for ch in name) % 14) * 0.1)
    return {
        "name": name,
        "price": int(price),
        "category": category,
        "description": description,
        "rating": round(rating, 1),
        "stock": int(stock),
        "sold_out": int(stock) <= 0,
    }


def normalize_menu_item(item, fallback_name="Food item"):
    if not isinstance(item, dict):
        return {
            "name": fallback_name,
            "price": 0,
            "category": "General",
            "description": "Freshly prepared food item.",
            "rating": 4.2,
            "stock": 25,
            "sold_out": False,
        }

    stock = item.get("stock")
    if stock is None:
        stock = 25

    sold_out = bool(item.get("sold_out", False))
    if int(stock) <= 0:
        sold_out = True

    rating = item.get("rating")
    if rating is None:
        rating = 3.8 + ((sum(ord(ch) for ch in str(item.get("name", fallback_name))) % 12) * 0.1)

    return {
        "name": item.get("name", fallback_name),
        "price": int(item.get("price", 0)),
        "category": item.get("category", "General"),
        "description": item.get("description", "Freshly prepared food item."),
        "rating": round(float(rating), 1),
        "stock": int(stock),
        "sold_out": sold_out,
    }


def normalize_restaurant_data(data):
    restaurants = data.get("restaurants", {})
    if not isinstance(restaurants, dict):
        return False

    changed = False
    for restaurant_name, restaurant in restaurants.items():
        if not isinstance(restaurant, dict):
            continue
        menu = restaurant.get("menu", {})
        if not isinstance(menu, dict):
            continue

        new_menu = {}
        for number, item in menu.items():
            new_menu[str(number)] = normalize_menu_item(item, fallback_name=f"{restaurant_name} item")

        if new_menu != menu:
            restaurant["menu"] = new_menu
            changed = True

    return changed


def guess_food_category(name):
    text = name.lower()
    if any(word in text for word in ["pizza", "bread", "fries", "pocket", "cake", "burger", "nugget", "nachos", "shake", "coffee"]):
        return "Fast Food"
    if any(word in text for word in ["noodles", "fried rice", "momos", "manchurian", "soup", "spring roll", "bhel"]):
        return "Chinese"
    if any(word in text for word in ["paneer", "dal", "biryani", "naan", "roti", "thali", "dosa", "curry", "masala", "pakora", "jamun", "rasmalai", "samosa"]):
        return "Indian"
    return "Special"


def guess_food_description(name):
    text = name.lower()
    if "pizza" in text:
        return "Freshly baked with a rich cheese layer and bold toppings."
    if "burger" in text:
        return "Hot, grilled, and packed with a satisfying crispy bite."
    if "noodles" in text or "fried rice" in text:
        return "Wok-tossed with aromatic sauces and crisp vegetables."
    if "paneer" in text or "dal" in text or "curry" in text:
        return "Slow-cooked with authentic spices and a comforting homemade taste."
    if "shake" in text or "coffee" in text:
        return "Chilled, creamy, and perfect to pair with your meal."
    if "fries" in text or "nachos" in text:
        return "Crispy, crunchy, and great as a quick snack side."
    return "Prepared fresh with a balanced mix of taste and quality ingredients."


def apply_realistic_food_defaults(data):
    changed = False
    for restaurant in data.get("restaurants", {}).values():
        if not isinstance(restaurant, dict):
            continue
        for item in restaurant.get("menu", {}).values():
            if not isinstance(item, dict):
                continue
            name = item.get("name", "Food Item")
            if "category" not in item or not item.get("category"):
                item["category"] = guess_food_category(name)
                changed = True
            if "description" not in item or not item.get("description"):
                item["description"] = guess_food_description(name)
                changed = True
            if "rating" not in item or item.get("rating") is None:
                value = 3.6 + ((sum(ord(ch) for ch in name) % 12) * 0.1)
                item["rating"] = round(value, 1)
                changed = True
            if "stock" not in item or item.get("stock") is None:
                item["stock"] = 6 + (sum(ord(ch) for ch in name) % 22)
                changed = True
            if item.get("stock", 0) <= 0:
                item["sold_out"] = True
            else:
                item["sold_out"] = False
    return changed


def get_coupon_value(data, code):
    if not code:
        return 0

    for coupon in data.get("coupons", []):
        if str(coupon.get("code", "")).upper() == str(code).upper():
            if coupon.get("type") == "percent":
                return int(coupon.get("value", 0))
            return int(coupon.get("value", 0))
    return 0


def get_backup_path():
    backup_dir = os.path.join(os.getcwd(), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_data_file(data):
    backup_dir = get_backup_path()
    file_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S.json")
    backup_path = os.path.join(backup_dir, file_name)
    with open(backup_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return backup_path


def restore_data_file(data, backup_path):
    if not os.path.exists(backup_path):
        error("Backup file not found.")
        return False

    with open(backup_path, "r", encoding="utf-8") as file:
        restored = json.load(file)

    for key, value in restored.items():
        data[key] = value

    save_data(data)
    return True


# ============================================================
# FOOD / RESTAURANTS
# ============================================================

def show_all_restaurants(data):
    header("RESTAURANTS", "🏪")
    print()

    restaurants = list(data["restaurants"].items())

    for index, (name, restaurant) in enumerate(restaurants, 1):
        available = restaurant["available_seats"]
        total = restaurant["total_seats"]
        print(f"{C.YELLOW}{index}.{C.RESET} {restaurant['emoji']} {C.BOLD}{name}{C.RESET}")
        print(f"     {seat_bar(available, total)}")

    print(f"\n{C.GREY}{len(restaurants) + 1}. 🔙 Back{C.RESET}")


def get_restaurant_by_number(data, choice):
    restaurants = list(data["restaurants"].items())

    try:
        index = int(choice) - 1
        if 0 <= index < len(restaurants):
            return restaurants[index]
    except ValueError:
        pass

    return None


def display_menu(restaurant_name, restaurant):
    header(restaurant_name.upper(), restaurant["emoji"])
    print()

    for number, item in restaurant["menu"].items():
        status = "SOLD OUT" if item.get("sold_out") or item.get("stock", 0) <= 0 else f"{item.get('stock', 0)} left"
        name_part = f"{C.YELLOW}{number}.{C.RESET} {item['name']}"
        price_part = money(item["price"])
        rating = f"⭐ {item.get('rating', 4.2):.1f}"
        print(f"  {name_part:<38} {price_part}  {C.GREY}{rating}{C.RESET}")
        if item.get("description"):
            print(f"     {C.GREY}{item['description']}{C.RESET}")
        print(f"     {C.GREY}{item.get('category', 'General')} | {status}{C.RESET}")

    print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
    small_line()


def browse_food(data, cart):
    while True:
        clear_screen()
        header("BROWSE FOOD", "🍔")

        search = input(f"\n{C.CYAN}🔎 Search food (or type 'back'): {C.RESET}").strip().lower()

        if search == "back":
            return

        found = []

        for restaurant_name, restaurant in data["restaurants"].items():
            for number, item in restaurant["menu"].items():
                haystack = " ".join([
                    item.get("name", "").lower(),
                    item.get("category", "").lower(),
                    item.get("description", "").lower(),
                    restaurant_name.lower(),
                ])
                if search in haystack:
                    found.append((restaurant_name, number, item))

        if not found:
            print()
            error("No food found.")
            pause()
            continue

        print()
        for index, (restaurant_name, number, item) in enumerate(found, 1):
            print(
                f"{C.YELLOW}{index}.{C.RESET} {item['name']} — {money(item['price'])}"
                f"  {C.GREY}| {restaurant_name}{C.RESET}"
            )

        print(f"{C.GREY}0. 🔙 Back{C.RESET}")

        choice = input(f"\n{C.CYAN}Enter food number to add to cart: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            restaurant_name, _, item = found[index]
        except (ValueError, IndexError):
            error("Invalid choice.")
            pause()
            continue

        add_to_cart(cart, restaurant_name, item)


def add_to_cart(cart, restaurant_name, item):
    if item.get("sold_out") or int(item.get("stock", 0)) <= 0:
        print()
        error(f"{item['name']} is sold out.")
        pause()
        return

    for cart_item in cart:
        if (
            cart_item["name"] == item["name"]
            and cart_item["restaurant"] == restaurant_name
        ):
            if cart_item["quantity"] >= int(item.get("stock", 99999)):
                print()
                error(f"Only {item.get('stock', 0)} of {item['name']} left.")
                pause()
                return
            cart_item["quantity"] += 1
            print()
            success(f"Increased {item['name']} quantity.")
            pause()
            return

    cart.append({
        "name": item["name"],
        "price": item["price"],
        "quantity": 1,
        "restaurant": restaurant_name
    })

    print()
    success(f"🛒 {item['name']} added to cart!")
    pause()


def restaurants(data, cart):
    while True:
        clear_screen()
        show_all_restaurants(data)

        choice = input(f"\n{C.CYAN}Enter restaurant number: {C.RESET}").strip()

        if choice == str(len(data["restaurants"]) + 1):
            return

        result = get_restaurant_by_number(data, choice)

        if result is None:
            error("Invalid restaurant choice.")
            pause()
            continue

        restaurant_name, restaurant = result

        while True:
            clear_screen()
            display_menu(restaurant_name, restaurant)

            food_choice = input(f"{C.CYAN}Enter dish number: {C.RESET}").strip()

            if food_choice == "0":
                break

            if food_choice not in restaurant["menu"]:
                error("Invalid dish number.")
                pause()
                continue

            item = restaurant["menu"][food_choice]
            add_to_cart(cart, restaurant_name, item)


# ============================================================
# CART
# ============================================================

def cart_total(cart):
    return sum(
        item["price"] * item["quantity"]
        for item in cart
    )


def show_cart(cart):
    header("YOUR CART", "🛒")
    print()

    if not cart:
        print(f"{C.GREY}Your cart is empty.{C.RESET}")
        return

    for index, item in enumerate(cart, 1):
        total = item["price"] * item["quantity"]

        print(f"{C.YELLOW}{index}.{C.RESET} {C.BOLD}{item['name']}{C.RESET}")
        print(
            f"   {C.GREY}{item['restaurant']}{C.RESET} | "
            f"{money(item['price'])} × {item['quantity']} = {money(total)}"
        )
        small_line()

    print(f"{C.BOLD}💰 Total: {money(cart_total(cart))}{C.RESET}")


def cart_menu(data, username, cart):
    while True:
        clear_screen()
        show_cart(cart)

        if not cart:
            pause()
            return

        menu_box([
            ("1", "➕ Add More Food"),
            ("2", "➖ Remove Item"),
            ("3", "🔢 Change Quantity"),
            ("4", "🧹 Clear Cart"),
            ("5", "💳 Checkout"),
            ("6", "🔙 Back"),
        ])

        choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if choice == "1":
            browse_food(data, cart)

        elif choice == "2":
            remove_cart_item(cart)

        elif choice == "3":
            change_quantity(cart)

        elif choice == "4":
            confirm = input(f"{C.YELLOW}Clear entire cart? (yes/no): {C.RESET}").lower()
            if confirm == "yes":
                cart.clear()
                success("Cart cleared.")
                pause()

        elif choice == "5":
            if checkout(data, username, cart):
                return

        elif choice == "6":
            return

        else:
            error("Invalid choice.")
            pause()


def remove_cart_item(cart):
    try:
        number = int(input(f"{C.CYAN}Enter item number to remove: {C.RESET}"))
        index = number - 1

        if 0 <= index < len(cart):
            removed = cart.pop(index)
            success(f"🗑️ Removed {removed['name']}.")
        else:
            error("Invalid item number.")

    except ValueError:
        error("Please enter a number.")

    pause()


def change_quantity(cart):
    try:
        number = int(input(f"{C.CYAN}Enter item number: {C.RESET}"))
        index = number - 1

        if not (0 <= index < len(cart)):
            error("Invalid item number.")
            pause()
            return

        quantity = int(input(f"{C.CYAN}Enter new quantity: {C.RESET}"))

        if quantity <= 0:
            cart.pop(index)
            success("🗑️ Item removed.")
        else:
            cart[index]["quantity"] = quantity
            success("Quantity updated.")

    except ValueError:
        error("Please enter valid numbers.")

    pause()


# ============================================================
# CHECKOUT / ORDERS
# ============================================================

def checkout(data, username, cart):
    user = data["users"][username]

    clear_screen()
    header("CHECKOUT", "💳")
    print()

    show_cart(cart)

    total = cart_total(cart)
    coupon_code = input(f"\n{C.CYAN}Coupon code (or type 'skip'): {C.RESET}").strip()
    coupon_discount = 0
    if coupon_code and coupon_code.lower() != "skip":
        coupon_discount = get_coupon_value(data, coupon_code)
        if coupon_discount:
            success(f"Coupon applied: {coupon_code}")
        else:
            error("Invalid coupon code.")
            coupon_discount = 0

    if coupon_discount > 0:
        if coupon_discount > 100:
            coupon_discount = 100
        total_after_coupon = total - (total * coupon_discount / 100 if coupon_code.upper().startswith("SAVE") else coupon_discount)
        total = max(0, round(total_after_coupon))
    else:
        total = total

    print(f"\n{C.WHITE}💰 Wallet Balance: {money(user['wallet'])}{C.RESET}")
    print(f"{C.WHITE}🧾 Amount to Pay : {money(total)}{C.RESET}")

    if user["wallet"] < total:
        print()
        error("Insufficient wallet balance.")
        info("Go to Profile → Wallet to add money.")
        pause()
        return False

    confirm = input(f"\n{C.YELLOW}Confirm order? (yes/no): {C.RESET}").lower()

    if confirm != "yes":
        warn("Order cancelled.")
        pause()
        return False

    user["wallet"] -= total

    order = {
        "id": generate_order_id(data),
        "username": username,
        "items": [dict(item) for item in cart],
        "total": total,
        "status": "Preparing",
        "date": datetime.now().strftime("%d-%m-%Y %I:%M %p")
    }

    data["orders"].append(order)
    user["orders"].append(order["id"])
    add_activity_log(data, "order_created", f"{username} placed {order['id']} for {money(total)}")

    # Food points: 1 point for every ₹10 spent.
    points = total // 10
    user["food_points"] += points

    save_data(data)

    print()
    line("═", C.GREEN)
    print(f"{C.GREEN}{C.BOLD}✅ ORDER PLACED SUCCESSFULLY!{C.RESET}")
    line("═", C.GREEN)
    print(f"🧾 Order ID: {C.BOLD}{order['id']}{C.RESET}")
    print(f"💰 Paid: {money(total)}")
    print(f"⭐ Food Points Earned: {C.YELLOW}{points}{C.RESET}")
    print(f"💳 Remaining Wallet: {money(user['wallet'])}")
    print(f"🟡 Status: {status_badge('Preparing')}")
    line("═", C.GREEN)

    cart.clear()
    pause()
    return True


def my_orders(data, username):
    clear_screen()
    header("MY ORDERS", "📦")
    print()

    orders = [
        order for order in data["orders"]
        if order["username"] == username
    ]

    if not orders:
        print(f"{C.GREY}You have not placed any orders yet.{C.RESET}")
        pause()
        return

    for order in reversed(orders):
        print(f"🧾 {C.BOLD}{order['id']}{C.RESET} {C.GREY}| {order['date']}{C.RESET}")
        print(f"Status: {status_badge(order['status'])}")
        print(f"Total: {money(order['total'])}")

        for item in order["items"]:
            print(f"  {C.GREY}•{C.RESET} {item['name']} × {item['quantity']}")

        small_line()

    pause()


# ============================================================
# SEATS / RESERVATIONS
# ============================================================

def available_seats(data, username):
    while True:
        clear_screen()
        show_all_restaurants(data)

        choice = input(f"\n{C.CYAN}Enter restaurant number: {C.RESET}").strip()

        if choice == str(len(data["restaurants"]) + 1):
            return

        result = get_restaurant_by_number(data, choice)

        if result is None:
            error("Invalid choice.")
            pause()
            continue

        restaurant_name, restaurant = result

        print(f"\n{restaurant['emoji']} {C.BOLD}{restaurant_name}{C.RESET}")
        print(f"🪑 Total seats     : {restaurant['total_seats']}")
        print(f"🟢 Available seats : {C.GREEN}{restaurant['available_seats']}{C.RESET}")
        print(
            f"🔴 Occupied seats  : "
            f"{C.RED}{restaurant['total_seats'] - restaurant['available_seats']}{C.RESET}"
        )
        print(f"   {seat_bar(restaurant['available_seats'], restaurant['total_seats'])}")

        if restaurant["available_seats"] <= 0:
            print()
            error("No seats are currently available.")
            pause()
            continue

        book = input(f"\n{C.YELLOW}Do you want to book seats? (yes/no): {C.RESET}").lower()

        if book != "yes":
            continue

        try:
            seats = int(input(f"{C.CYAN}How many seats? {C.RESET}"))

            if seats <= 0:
                error("Number of seats must be greater than 0.")
            elif seats > restaurant["available_seats"]:
                error("Not enough seats available.")
            else:
                restaurant["available_seats"] -= seats

                reservation = {
                    "id": generate_reservation_id(data),
                    "username": username,
                    "restaurant": restaurant_name,
                    "seats": seats,
                    "date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    "status": "Confirmed"
                }

                data["users"][username]["reservations"].append(
                    reservation["id"]
                )

                if "reservations" not in data:
                    data["reservations"] = []

                data["reservations"].append(reservation)

                save_data(data)

                print()
                success("Reservation confirmed!")
                print(f"🧾 Reservation ID: {C.BOLD}{reservation['id']}{C.RESET}")
                print(f"🏪 Restaurant: {restaurant_name}")
                print(f"🪑 Seats: {seats}")
                print(f"🟢 Remaining seats: {C.GREEN}{restaurant['available_seats']}{C.RESET}")

        except ValueError:
            error("Please enter a valid number.")

        pause()


def my_reservations(data, username):
    clear_screen()
    header("MY RESERVATIONS", "📅")
    print()

    reservations = data.get("reservations", [])

    mine = [
        reservation for reservation in reservations
        if reservation["username"] == username
    ]

    if not mine:
        print(f"{C.GREY}No reservations found.{C.RESET}")
        pause()
        return

    for reservation in reversed(mine):
        print(f"🧾 {C.BOLD}{reservation['id']}{C.RESET}")
        print(f"🏪 {reservation['restaurant']}")
        print(f"🪑 Seats: {reservation['seats']}")
        print(f"📅 {reservation['date']}")
        print(f"Status: {status_badge(reservation['status'])}")
        small_line()

    pause()


# ============================================================
# FAVORITES
# ============================================================

def favorites(data, username):
    user = data["users"][username]

    while True:
        clear_screen()
        header("FAVORITES", "❤️")
        print()

        if not user["favorites"]:
            print(f"{C.GREY}No favorite food yet.{C.RESET}")
        else:
            for index, item in enumerate(user["favorites"], 1):
                print(
                    f"{C.YELLOW}{index}.{C.RESET} {item['name']} — {money(item['price'])}"
                    f" {C.GREY}| {item['restaurant']}{C.RESET}"
                )

        print()
        menu_box([
            ("1", "❤️ Add Favorite"),
            ("2", "🗑️ Remove Favorite"),
            ("3", "🔙 Back"),
        ])

        choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if choice == "1":
            add_favorite(data, username)

        elif choice == "2":
            remove_favorite(data, username)

        elif choice == "3":
            return

        else:
            error("Invalid choice.")
            pause()


def add_favorite(data, username):
    user = data["users"][username]

    clear_screen()
    sub_header("ADD FAVORITE", "❤️")
    print()

    all_food = []

    for restaurant_name, restaurant in data["restaurants"].items():
        for number, item in restaurant["menu"].items():
            all_food.append((restaurant_name, item))

    for index, (restaurant_name, item) in enumerate(all_food, 1):
        print(
            f"{C.YELLOW}{index}.{C.RESET} {item['name']} — {money(item['price'])}"
            f" {C.GREY}| {restaurant_name}{C.RESET}"
        )

    try:
        choice = int(input(f"\n{C.CYAN}Choose food: {C.RESET}"))
        restaurant_name, item = all_food[choice - 1]

        favorite = {
            "name": item["name"],
            "price": item["price"],
            "restaurant": restaurant_name
        }

        if favorite not in user["favorites"]:
            user["favorites"].append(favorite)
            save_data(data)
            success("Added to favorites!")
        else:
            warn("Already in favorites.")

    except (ValueError, IndexError):
        error("Invalid choice.")

    pause()


def remove_favorite(data, username):
    user = data["users"][username]

    if not user["favorites"]:
        print(f"{C.GREY}No favorites to remove.{C.RESET}")
        pause()
        return

    try:
        choice = int(input(f"{C.CYAN}Enter favorite number: {C.RESET}"))
        removed = user["favorites"].pop(choice - 1)
        save_data(data)
        success(f"🗑️ Removed {removed['name']}.")

    except (ValueError, IndexError):
        error("Invalid choice.")

    pause()


# ============================================================
# WALLET
# ============================================================

def wallet(data, username):
    user = data["users"][username]

    while True:
        clear_screen()
        header("WALLET", "💰")
        print()

        print(f"Current Balance: {money(user['wallet'])}")
        print(f"⭐ Food Points : {C.YELLOW}{user['food_points']}{C.RESET}")

        print()
        menu_box([
            ("1", "➕ Add Money"),
            ("2", "⭐ View Food Points"),
            ("3", "🔙 Back"),
        ])

        choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if choice == "1":
            try:
                amount = int(input(f"{C.CYAN}Enter amount to add: {C.RESET}"))

                if amount <= 0:
                    error("Amount must be greater than 0.")
                else:
                    user["wallet"] += amount
                    save_data(data)
                    success(f"{money_plain(amount)} added to wallet!")

            except ValueError:
                error("Enter a valid amount.")

            pause()

        elif choice == "2":
            print(f"\n⭐ You have {C.YELLOW}{user['food_points']}{C.RESET} Food Points.")
            pause()

        elif choice == "3":
            return

        else:
            error("Invalid choice.")
            pause()


# ============================================================
# REVIEWS
# ============================================================

def reviews(data, username):
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
            restaurant_names = list(data["restaurants"].keys())
            print()

            for index, name in enumerate(restaurant_names, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {name}")

            try:
                restaurant_number = int(
                    input(f"\n{C.CYAN}Choose restaurant: {C.RESET}")
                )
                restaurant_name = restaurant_names[
                    restaurant_number - 1
                ]

                rating = int(input(f"{C.CYAN}Rating (1-5): {C.RESET}"))

                if not 1 <= rating <= 5:
                    error("Rating must be between 1 and 5.")
                    pause()
                    continue

                comment = input(f"{C.CYAN}Write your review: {C.RESET}").strip()

                review = {
                    "username": username,
                    "restaurant": restaurant_name,
                    "rating": rating,
                    "comment": comment,
                    "date": datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    )
                }

                data["reviews"].append(review)
                data["users"][username]["reviews"].append(review)

                save_data(data)

                print()
                success("Thank you for your review!")

            except (ValueError, IndexError):
                error("Invalid input.")

            pause()

        elif choice == "2":
            user_reviews = data["users"][username]["reviews"]
            print()

            if not user_reviews:
                print(f"{C.GREY}You have not written any reviews.{C.RESET}")
            else:
                for review in user_reviews:
                    stars = "★" * review["rating"] + "☆" * (5 - review["rating"])
                    print(
                        f"\n🏪 {C.BOLD}{review['restaurant']}{C.RESET}"
                        f"\n{C.YELLOW}{stars}{C.RESET} ({review['rating']}/5)"
                        f"\n💬 {review['comment']}"
                        f"\n{C.GREY}📅 {review['date']}{C.RESET}"
                    )
                    small_line()

            pause()

        elif choice == "3":
            return

        else:
            error("Invalid choice.")
            pause()


# ============================================================
# PROFILE
# ============================================================

def profile(data, username):
    user = data["users"][username]

    while True:
        clear_screen()
        header("PROFILE", "👤")
        print()

        print(f"Name        : {C.BOLD}{user['name']}{C.RESET}")
        print(f"Username    : {username}")
        print(f"Wallet      : {money(user['wallet'])}")
        print(f"Food Points : {C.YELLOW}{user['food_points']}{C.RESET}")
        print(f"Favorites   : {len(user['favorites'])}")
        print(f"Orders      : {len(user['orders'])}")
        print(f"Reviews     : {len(user['reviews'])}")

        print()
        menu_box([
            ("1", "✏️ Change Name"),
            ("2", "🔐 Change Password"),
            ("3", "🔙 Back"),
        ])

        choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if choice == "1":
            new_name = input(f"{C.CYAN}Enter new name: {C.RESET}").strip()

            if new_name:
                user["name"] = new_name
                save_data(data)
                success("Name updated.")
            else:
                error("Name cannot be empty.")

            pause()

        elif choice == "2":
            old = input(f"{C.CYAN}Current password: {C.RESET}")

            if old != user["password"]:
                error("Wrong password.")
            else:
                new_password = input(f"{C.CYAN}New password: {C.RESET}")

                if new_password:
                    user["password"] = new_password
                    save_data(data)
                    success("Password changed.")
                else:
                    error("Password cannot be empty.")

            pause()

        elif choice == "3":
            return

        else:
            error("Invalid choice.")
            pause()


# ============================================================
# ANNOUNCEMENTS
# ============================================================

def notifications(data):
    clear_screen()
    header("ANNOUNCEMENTS", "🔔")
    print()

    for announcement in data["announcements"]:
        print(f"{C.YELLOW}📢{C.RESET} {announcement}")

    pause()


# ============================================================
# USER PORTAL
# ============================================================

def user_portal(data, username):
    cart = []

    while True:
        clear_screen()
        user = data["users"][username]

        header("USER PORTAL", "👤")
        print(f"\nWelcome, {C.BOLD}{user['name']}{C.RESET}! 👋")
        print(
            f"💰 Wallet: {money(user['wallet'])}"
            f"   ⭐ Points: {C.YELLOW}{user['food_points']}{C.RESET}"
        )
        print()

        menu_box([
            ("1", "🍔 Browse Food"),
            ("2", "🏪 Restaurants"),
            ("3", "🛒 Cart"),
            ("4", "🪑 Available Seats"),
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
            browse_food(data, cart)

        elif choice == "2":
            restaurants(data, cart)

        elif choice == "3":
            cart_menu(data, username, cart)

        elif choice == "4":
            available_seats(data, username)

        elif choice == "5":
            my_reservations(data, username)

        elif choice == "6":
            my_orders(data, username)

        elif choice == "7":
            favorites(data, username)

        elif choice == "8":
            wallet(data, username)

        elif choice == "9":
            reviews(data, username)

        elif choice == "10":
            notifications(data)

        elif choice == "11":
            profile(data, username)

        elif choice == "12":
            print()
            success("Logged out successfully.")
            pause()
            return

        else:
            error("Invalid choice.")
            pause()


# ============================================================
# REGISTER / LOGIN
# ============================================================

def register(data):
    clear_screen()
    header("CREATE ACCOUNT", "📝")
    print()

    username = input(f"{C.CYAN}Choose username: {C.RESET}").strip().lower()

    if not username:
        error("Username cannot be empty.")
        pause()
        return

    if username in data["users"]:
        error("Username already exists.")
        pause()
        return

    name = input(f"{C.CYAN}Your name: {C.RESET}").strip()
    password = input(f"{C.CYAN}Create password: {C.RESET}").strip()

    if not name or not password:
        error("Name and password cannot be empty.")
        pause()
        return

    data["users"][username] = {
        "password": hash_password(password),
        "name": name,
        "wallet": 500,
        "food_points": 0,
        "favorites": [],
        "reservations": [],
        "orders": [],
        "reviews": []
    }

    add_activity_log(data, "user_registered", username)
    save_data(data)

    print()
    success("Account created successfully!")
    print(f"💰 Starting wallet balance: {money(500)}")
    pause()


def login(data):
    clear_screen()
    header("LOGIN", "🔐")
    print()

    username = input(f"{C.CYAN}Username: {C.RESET}").strip().lower()
    password = input(f"{C.CYAN}Password: {C.RESET}").strip()

    user = data["users"].get(username)

    if user and verify_password(password, user["password"]):
        print()
        success("Login successful!")
        print(f"Welcome back, {C.BOLD}{user['name']}{C.RESET} 👋")
        add_activity_log(data, "user_login", username)
        save_data(data)
        pause()
        user_portal(data, username)
    else:
        print()
        error("Invalid username or password.")
        pause()


# ============================================================
# ADMIN PORTAL
# ============================================================

def admin_login():
    username = input(f"{C.CYAN}Admin username: {C.RESET}").strip()
    password = input(f"{C.CYAN}Admin password: {C.RESET}").strip()

    return username == "admin" and password == "admin123"


def admin_activity_logs(data):
    clear_screen()
    header("ACTIVITY LOGS", "📜")
    print()
    logs = data.get("activity_logs", [])

    if not logs:
        print(f"{C.GREY}No activity recorded yet.{C.RESET}")
    else:
        for entry in reversed(logs[-20:]):
            print(f"{C.GREY}{entry.get('time', '')}{C.RESET} | {C.BOLD}{entry.get('username', 'system')}{C.RESET} | {entry.get('action', '')}")
            if entry.get("details"):
                print(f"   {C.WHITE}{entry['details']}{C.RESET}")
            small_line()

    pause()


def delete_user_account(data, username):
    if username in data["users"]:
        del data["users"][username]
        save_data(data)
        success(f"User '{username}' deleted.")
        return True
    error("User not found.")
    return False


def admin_users(data):
    while True:
        clear_screen()
        header("MANAGE USERS", "👥")
        print()

        users = list(data["users"].items())
        if not users:
            print(f"{C.GREY}No users found.{C.RESET}")
            print(f"{C.GREY}0. 🔙 Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            if choice == "0":
                return
            error("Invalid choice.")
            pause()
            continue

        for index, (username, user) in enumerate(users, 1):
            print(
                f"{C.YELLOW}{index}.{C.RESET} 👤 {C.BOLD}{username}{C.RESET}"
                f" | {user['name']} | Wallet: {money(user['wallet'])}"
            )

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose user number to delete: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            username, user = users[index]
        except (ValueError, IndexError):
            error("Invalid user choice.")
            pause()
            continue

        confirm = input(
            f"{C.YELLOW}Delete user '{username}' ({user['name']})? (yes/no): {C.RESET}"
        ).strip().lower()

        if confirm == "yes":
            delete_user_account(data, username)
        else:
            warn("User deletion cancelled.")

        pause()


def admin_restaurants(data):
    while True:
        clear_screen()
        header("MANAGE RESTAURANTS", "🏪")
        print()

        restaurants = list(data["restaurants"].items())

        if not restaurants:
            print(f"{C.GREY}No restaurants found.{C.RESET}")
            print(f"{C.GREY}0. 🔙 Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            if choice == "0":
                return
            error("Invalid choice.")
            pause()
            continue

        for index, (name, restaurant) in enumerate(restaurants, 1):
            print(
                f"{C.YELLOW}{index}.{C.RESET} {restaurant['emoji']} {C.BOLD}{name}{C.RESET}"
                f" | Seats: {restaurant['available_seats']}/{restaurant['total_seats']}"
                f" | {seat_bar(restaurant['available_seats'], restaurant['total_seats'], 10)}"
            )

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose restaurant: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            restaurant_name, restaurant = restaurants[index]
        except (ValueError, IndexError):
            error("Invalid restaurant choice.")
            pause()
            continue

        while True:
            clear_screen()
            header(f"{restaurant_name.upper()} MENU", restaurant["emoji"])
            print()
            print(f"Seats: {C.GREEN}{restaurant['available_seats']}{C.RESET}/{restaurant['total_seats']}")
            print(f"Status: {C.BOLD}{('Open' if restaurant['available_seats'] > 0 else 'Closed')}{C.RESET}")
            print()

            menu_box([
                ("1", "🔄 Refill seats"),
                ("2", "🪑 Set available seats"),
                ("3", "📋 View menu"),
                ("4", "🔙 Back"),
            ])

            action = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

            if action == "1":
                restaurant["available_seats"] = restaurant["total_seats"]
                save_data(data)
                success(f"Seats refilled for {restaurant_name}.")
                pause()
                break

            elif action == "2":
                try:
                    seats = int(input(f"{C.CYAN}Enter available seats: {C.RESET}").strip())
                    if seats < 0 or seats > restaurant["total_seats"]:
                        raise ValueError
                    restaurant["available_seats"] = seats
                    save_data(data)
                    success(f"Available seats updated for {restaurant_name}.")
                except ValueError:
                    error(f"Please enter a number between 0 and {restaurant['total_seats']}.")
                pause()
                break

            elif action == "3":
                clear_screen()
                header(f"{restaurant_name.upper()} MENU", restaurant["emoji"])
                print()
                for number, item in restaurant["menu"].items():
                    print(f"{C.YELLOW}{number}.{C.RESET} {item['name']} — {money(item['price'])}")
                pause()
                continue

            elif action == "4":
                break

            else:
                error("Invalid choice.")
                pause()


def admin_orders(data):
    while True:
        clear_screen()
        header("MANAGE ORDERS", "📦")
        print()

        if not data["orders"]:
            print(f"{C.GREY}No orders yet.{C.RESET}")
            print(f"{C.GREY}0. 🔙 Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            if choice == "0":
                return
            error("Invalid choice.")
            pause()
            continue

        for index, order in enumerate(reversed(data["orders"]), 1):
            print(
                f"{C.YELLOW}{index}.{C.RESET} {C.BOLD}{order['id']}{C.RESET} | "
                f"{order['username']} | {money(order['total'])} | "
                f"{status_badge(order['status'])}"
            )

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose order number to update: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            order_index = len(data["orders"]) - int(choice)
            order = data["orders"][order_index]
        except (ValueError, IndexError):
            error("Invalid order choice.")
            pause()
            continue

        print()
        print(f"Update status for {C.BOLD}{order['id']}{C.RESET}:")
        status_options = ["Preparing", "Confirmed", "Ready", "Delivered", "Cancelled"]
        for i, status in enumerate(status_options, 1):
            print(f"{C.YELLOW}{i}.{C.RESET} {status_badge(status)}")

        try:
            status_choice = int(input(f"\n{C.CYAN}Choose new status: {C.RESET}").strip())
            new_status = status_options[status_choice - 1]
        except (ValueError, IndexError):
            error("Invalid status choice.")
            pause()
            continue

        order["status"] = new_status
        save_data(data)
        success(f"Order {order['id']} status updated to {status_badge(new_status)}.")
        pause()


def admin_revenue(data):
    clear_screen()
    header("REVENUE DASHBOARD", "💰")
    print()

    orders = data.get("orders", [])
    total_revenue = 0
    status_counts = {
        "Preparing": 0,
        "Confirmed": 0,
        "Ready": 0,
        "Delivered": 0,
        "Cancelled": 0,
    }
    top_items = {}
    highest_order = {"id": "N/A", "total": 0}

    for order in orders:
        total = int(order.get("total", 0))
        total_revenue += total

        status = order.get("status", "Preparing")
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts["Preparing"] += 1

        if total > highest_order["total"]:
            highest_order = {
                "id": order.get("id", "N/A"),
                "total": total,
            }

        for item in order.get("items", []):
            name = item.get("name", "Unknown")
            qty = int(item.get("quantity", 0))
            top_items[name] = top_items.get(name, 0) + qty

    total_orders = len(orders)
    average_order = total_revenue / total_orders if total_orders else 0
    completed_orders = status_counts.get("Delivered", 0)
    active_orders = status_counts.get("Preparing", 0) + status_counts.get("Confirmed", 0) + status_counts.get("Ready", 0)

    best_item = "N/A"
    best_item_count = 0
    if top_items:
        best_item, best_item_count = max(top_items.items(), key=lambda item: item[1])

    print(f"{C.BOLD}{C.YELLOW}TOTAL REVENUE{C.RESET}: {money(total_revenue)}")
    print(f"{C.BOLD}{C.YELLOW}TOTAL ORDERS{C.RESET}: {total_orders}")
    print(f"{C.BOLD}{C.YELLOW}AVERAGE ORDER{C.RESET}: {money(round(average_order))}")
    print(f"{C.BOLD}{C.YELLOW}DELIVERED ORDERS{C.RESET}: {completed_orders}")
    print(f"{C.BOLD}{C.YELLOW}ACTIVE ORDERS{C.RESET}: {active_orders}")
    print(f"{C.BOLD}{C.YELLOW}HIGHEST ORDER{C.RESET}: {highest_order['id']} ({money(highest_order['total'])})")

    if best_item != "N/A":
        print(f"{C.BOLD}{C.YELLOW}TOP ITEM{C.RESET}: {best_item} × {best_item_count}")

    print()
    print(f"{C.GREY}STATUS BREAKDOWN{C.RESET}")
    for status, count in status_counts.items():
        if count > 0:
            print(f"  {status_badge(status)}: {count}")

    if total_orders == 0:
        print(f"{C.GREY}No orders have been placed yet.{C.RESET}")

    pause()


def admin_announcements(data):
    clear_screen()
    header("SEND ANNOUNCEMENT", "🔔")
    print()

    message = input(f"{C.CYAN}Enter announcement: {C.RESET}").strip()

    if message:
        data["announcements"].append(message)
        save_data(data)
        success("Announcement sent.")
    else:
        error("Announcement cannot be empty.")

    pause()


def admin_food(data):
    while True:
        clear_screen()
        header("MANAGE FOOD", "🍔")
        print()

        restaurants = list(data["restaurants"].items())
        for index, (name, restaurant) in enumerate(restaurants, 1):
            print(f"{C.YELLOW}{index}.{C.RESET} {restaurant['emoji']} {C.BOLD}{name}{C.RESET} | {len(restaurant['menu'])} items")

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose restaurant: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            restaurant_index = int(choice) - 1
            restaurant_name, restaurant = restaurants[restaurant_index]
        except (ValueError, IndexError):
            error("Invalid restaurant choice.")
            pause()
            continue

        while True:
            clear_screen()
            header(f"{restaurant_name} FOOD", restaurant["emoji"])
            print()

            for number, item in restaurant["menu"].items():
                stock = item.get("stock", 0)
                status = "Sold Out" if item.get("sold_out") or stock <= 0 else f"{stock} left"
                print(f"{C.YELLOW}{number}.{C.RESET} {item['name']} | {money(item['price'])} | {status} | {item.get('category', 'General')}")

            print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
            print(f"{C.GREY}1. Add Item{C.RESET}")
            print(f"{C.GREY}2. Edit Item{C.RESET}")
            print(f"{C.GREY}3. Delete Item{C.RESET}")
            action = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

            if action == "0":
                break

            if action == "1":
                item_name = input(f"{C.CYAN}Item name: {C.RESET}").strip()
                if not item_name:
                    error("Item name cannot be empty.")
                    pause()
                    continue

                try:
                    price = int(input(f"{C.CYAN}Price: {C.RESET}").strip())
                    stock = int(input(f"{C.CYAN}Stock: {C.RESET}").strip())
                    category = input(f"{C.CYAN}Category: {C.RESET}").strip() or "General"
                    description = input(f"{C.CYAN}Description: {C.RESET}").strip() or "Freshly prepared food item."
                except ValueError:
                    error("Price and stock must be valid numbers.")
                    pause()
                    continue

                item_number = str(max([int(x) for x in restaurant["menu"].keys()] + [0]) + 1)
                restaurant["menu"][item_number] = {
                    "name": item_name,
                    "price": price,
                    "category": category,
                    "description": description,
                    "rating": 4.2,
                    "stock": stock,
                    "sold_out": stock <= 0,
                }
                save_data(data)
                success(f"Added {item_name} to {restaurant_name}.")
                pause()

            elif action == "2":
                item_number = input(f"{C.CYAN}Enter item number to edit: {C.RESET}").strip()
                if item_number not in restaurant["menu"]:
                    error("Item not found.")
                    pause()
                    continue

                item = restaurant["menu"][item_number]
                item["name"] = input(f"{C.CYAN}New name ({item['name']}): {C.RESET}").strip() or item["name"]
                item["price"] = int(input(f"{C.CYAN}New price ({item['price']}): {C.RESET}").strip() or item["price"])
                item["category"] = input(f"{C.CYAN}New category ({item['category']}): {C.RESET}").strip() or item["category"]
                item["description"] = input(f"{C.CYAN}New description ({item['description']}): {C.RESET}").strip() or item["description"]
                item["stock"] = int(input(f"{C.CYAN}New stock ({item.get('stock', 0)}): {C.RESET}").strip() or item.get("stock", 0))
                item["sold_out"] = item["stock"] <= 0
                save_data(data)
                success(f"Updated {item['name']}.")
                pause()

            elif action == "3":
                item_number = input(f"{C.CYAN}Enter item number to delete: {C.RESET}").strip()
                if item_number not in restaurant["menu"]:
                    error("Item not found.")
                    pause()
                    continue

                removed = restaurant["menu"].pop(item_number)
                save_data(data)
                success(f"Deleted {removed['name']}.")
                pause()

            else:
                error("Invalid choice.")
                pause()


def admin_tables(data):
    while True:
        clear_screen()
        header("MANAGE TABLES", "🪑")
        print()

        restaurants = list(data["restaurants"].items())
        for index, (name, restaurant) in enumerate(restaurants, 1):
            print(f"{C.YELLOW}{index}.{C.RESET} {restaurant['emoji']} {C.BOLD}{name}{C.RESET} | Seats: {restaurant['available_seats']}/{restaurant['total_seats']}")

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose restaurant: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            restaurant_index = int(choice) - 1
            restaurant_name, restaurant = restaurants[restaurant_index]
        except (ValueError, IndexError):
            error("Invalid restaurant choice.")
            pause()
            continue

        while True:
            clear_screen()
            header(f"{restaurant_name} TABLES", "🪑")
            print()
            print(f"Total seats: {restaurant['total_seats']}")
            print(f"Available seats: {restaurant['available_seats']}")
            print()

            menu_box([
                ("1", "🔄 Refill Seats"),
                ("2", "🪑 Set Available Seats"),
                ("3", "📏 Set Total Seats"),
                ("4", "🔙 Back"),
            ])

            action = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

            if action == "1":
                restaurant["available_seats"] = restaurant["total_seats"]
                save_data(data)
                success(f"Seats refilled for {restaurant_name}.")
                pause()
                break

            elif action == "2":
                try:
                    seats = int(input(f"{C.CYAN}Set available seats: {C.RESET}").strip())
                    if seats < 0 or seats > restaurant["total_seats"]:
                        raise ValueError
                    restaurant["available_seats"] = seats
                    save_data(data)
                    success(f"Available seats updated.")
                except ValueError:
                    error(f"Enter a number between 0 and {restaurant['total_seats']}.")
                pause()
                break

            elif action == "3":
                try:
                    total = int(input(f"{C.CYAN}Set total seats: {C.RESET}").strip())
                    if total <= 0:
                        raise ValueError
                    restaurant["total_seats"] = total
                    restaurant["available_seats"] = min(restaurant["available_seats"], total)
                    save_data(data)
                    success(f"Total seats updated to {total}.")
                except ValueError:
                    error("Total seats must be a positive number.")
                pause()
                break

            elif action == "4":
                break

            else:
                error("Invalid choice.")
                pause()


def admin_coupons(data):
    while True:
        clear_screen()
        header("MANAGE COUPONS", "🎟️")
        print()

        for index, coupon in enumerate(data.get("coupons", []), 1):
            print(f"{C.YELLOW}{index}.{C.RESET} {coupon['code']} | {coupon['description']} | {coupon['value']} {coupon['type']}")

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        print(f"{C.GREY}1. Add Coupon{C.RESET}")
        print(f"{C.GREY}2. Edit Coupon{C.RESET}")
        print(f"{C.GREY}3. Delete Coupon{C.RESET}")
        action = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if action == "0":
            return

        if action == "1":
            code = input(f"{C.CYAN}Coupon code: {C.RESET}").strip().upper()
            kind = input(f"{C.CYAN}Type (percent/flat): {C.RESET}").strip().lower()
            value = int(input(f"{C.CYAN}Value: {C.RESET}").strip())
            description = input(f"{C.CYAN}Description: {C.RESET}").strip() or "Special offer"
            data.setdefault("coupons", []).append({"code": code, "type": kind, "value": value, "description": description})
            save_data(data)
            success(f"Coupon {code} added.")
            pause()

        elif action == "2":
            try:
                idx = int(input(f"{C.CYAN}Choose coupon number: {C.RESET}").strip()) - 1
                coupon = data["coupons"][idx]
                coupon["code"] = input(f"{C.CYAN}Code ({coupon['code']}): {C.RESET}").strip().upper() or coupon["code"]
                coupon["type"] = input(f"{C.CYAN}Type ({coupon['type']}): {C.RESET}").strip().lower() or coupon["type"]
                coupon["value"] = int(input(f"{C.CYAN}Value ({coupon['value']}): {C.RESET}").strip() or coupon["value"])
                coupon["description"] = input(f"{C.CYAN}Description ({coupon['description']}): {C.RESET}").strip() or coupon["description"]
                save_data(data)
                success("Coupon updated.")
            except (ValueError, IndexError):
                error("Invalid coupon selection.")
            pause()

        elif action == "3":
            try:
                idx = int(input(f"{C.CYAN}Choose coupon number to delete: {C.RESET}").strip()) - 1
                removed = data["coupons"].pop(idx)
                save_data(data)
                success(f"Deleted coupon {removed['code']}.")
            except (ValueError, IndexError):
                error("Invalid coupon selection.")
            pause()

        else:
            error("Invalid choice.")
            pause()


def admin_reviews(data):
    while True:
        clear_screen()
        header("MANAGE REVIEWS", "⭐")
        print()

        reviews = data.get("reviews", [])
        if not reviews:
            print(f"{C.GREY}No reviews yet.{C.RESET}")
            print(f"{C.GREY}0. 🔙 Back{C.RESET}")
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            if choice == "0":
                return
            pause()
            continue

        for index, review in enumerate(reviews, 1):
            stars = "★" * review["rating"] + "☆" * (5 - review["rating"])
            print(f"{C.YELLOW}{index}.{C.RESET} {review['username']} | {review['restaurant']} | {stars}")
            print(f"  {C.GREY}{review['comment']}{C.RESET}")

        print(f"\n{C.GREY}0. 🔙 Back{C.RESET}")
        choice = input(f"\n{C.CYAN}Choose review to delete: {C.RESET}").strip()

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            review = reviews.pop(idx)
            for user in data["users"].values():
                current_reviews = user.get("reviews", [])
                if isinstance(current_reviews, list):
                    user["reviews"] = [
                        r for r in current_reviews
                        if r.get("comment") != review.get("comment")
                        or r.get("restaurant") != review.get("restaurant")
                        or r.get("username") != review.get("username")
                    ]
            save_data(data)
            success(f"Review from {review['username']} removed.")
        except (ValueError, IndexError):
            error("Invalid review choice.")

        pause()


def admin_settings(data):
    while True:
        clear_screen()
        header("SETTINGS", "⚙️")
        print()

        menu_box([
            ("1", "💾 Backup Data"),
            ("2", "📂 Restore Data"),
            ("3", "🗂️ View Backups"),
            ("4", "🔙 Back"),
        ])

        action = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if action == "1":
            backup_path = backup_data_file(data)
            success(f"Backup created at: {backup_path}")
            pause()
            continue

        elif action == "2":
            backup_dir = get_backup_path()
            files = [os.path.join(backup_dir, name) for name in sorted(os.listdir(backup_dir)) if name.endswith(".json")]
            if not files:
                error("No backup files found.")
                pause()
                continue

            for index, file_path in enumerate(files, 1):
                print(f"{C.YELLOW}{index}.{C.RESET} {file_path}")
            try:
                choice = int(input(f"\n{C.CYAN}Choose backup file: {C.RESET}").strip()) - 1
                restored = restore_data_file(data, files[choice])
                if restored:
                    success("Data restored successfully.")
            except (ValueError, IndexError):
                error("Invalid backup selection.")
            pause()
            continue

        elif action == "3":
            backup_dir = get_backup_path()
            files = [name for name in sorted(os.listdir(backup_dir)) if name.endswith(".json")]
            if not files:
                print(f"{C.GREY}No backups found.{C.RESET}")
            else:
                for file_name in files:
                    print(f"{C.YELLOW}•{C.RESET} {file_name}")
            pause()
            continue

        elif action == "4":
            return

        else:
            error("Invalid choice.")
            pause()


def admin_portal(data):
    while True:
        clear_screen()
        header("ADMIN PORTAL", "👑")
        print()

        menu_box([
            ("1", "👥 Manage Users"),
            ("2", "🏪 Manage Restaurants"),
            ("3", "🍔 Manage Food"),
            ("4", "🪑 Manage Tables"),
            ("5", "📦 Manage Orders"),
            ("6", "🎟️ Manage Coupons"),
            ("7", "⭐ Manage Reviews"),
            ("8", "💰 Revenue"),
            ("9", "📊 Statistics"),
            ("10", "🔔 Announcements"),
            ("11", "📜 Activity Logs"),
            ("12", "⚙️ Settings"),
            ("13", "🚪 Logout"),
        ])

        choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()

        if choice == "1":
            admin_users(data)

        elif choice == "2":
            admin_restaurants(data)

        elif choice == "3":
            admin_food(data)

        elif choice == "4":
            admin_tables(data)

        elif choice == "5":
            admin_orders(data)

        elif choice == "6":
            admin_coupons(data)

        elif choice == "7":
            admin_reviews(data)

        elif choice == "8":
            admin_revenue(data)

        elif choice == "9":
            clear_screen()
            header("STATISTICS", "📊")
            print()
            print(f"👥 Users: {C.BOLD}{len(data['users'])}{C.RESET}")
            print(f"🏪 Restaurants: {C.BOLD}{len(data['restaurants'])}{C.RESET}")
            print(f"📦 Orders: {C.BOLD}{len(data['orders'])}{C.RESET}")
            print(f"⭐ Reviews: {C.BOLD}{len(data['reviews'])}{C.RESET}")
            print(f"📜 Activity Logs: {C.BOLD}{len(data.get('activity_logs', []))}{C.RESET}")
            pause()

        elif choice == "10":
            admin_announcements(data)

        elif choice == "11":
            admin_activity_logs(data)

        elif choice == "12":
            admin_settings(data)

        elif choice == "13":
            return

        else:
            error("Invalid choice.")
            pause()


# ============================================================
# MAIN
# ============================================================

def main():
    data = load_data()

    while True:
        clear_screen()

        print(f"{C.ORANGE}{C.BOLD}")
        header("ALAKH DA DHAABA", "🍽️")
        print(f"{C.RESET}", end="")
        print(f"{C.GREY}{'FOOD COURT MANAGEMENT SYSTEM'.center(_width())}{C.RESET}")
        print()

        menu_box([
            ("1", "🔐 User Login"),
            ("2", "📝 Create Account"),
            ("3", "👑 Admin Login"),
            ("4", "🚪 Exit"),
        ])

        choice = input(f"\n{C.CYAN}Enter your choice: {C.RESET}").strip()

        if choice == "1":
            login(data)

        elif choice == "2":
            register(data)

        elif choice == "3":
            clear_screen()
            header("ADMIN LOGIN", "👑")
            print()

            if admin_login():
                print()
                success("Admin login successful.")
                pause()
                admin_portal(data)
            else:
                print()
                error("Invalid admin credentials.")
                pause()

        elif choice == "4":
            print()
            success("Thank you for visiting Alakh Da Dhaaba!")
            print(f"{C.CYAN}👋 See you again!{C.RESET}")
            break

        else:
            error("Please choose a valid option.")
            pause()


if __name__ == "__main__":
    main()

