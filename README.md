# 🍽️ Alakh Da Dhaaba — Food Court Management System

A colorful, menu-driven **command-line food court app** built entirely with the Python standard library. No frameworks, no database server — just clean terminal UI and a JSON file for permanent storage.

Think of it as a mini food-delivery platform (browse → cart → checkout → track order) plus a full admin back-office, all running in your terminal.

---

## ✨ Features

### 👤 User side
- **Account system** — register, log in, change name/password
- **Browse & search food** across all restaurants, with live search-as-you-type filtering
- **Cart** — add, remove, adjust quantities, clear, checkout
- **Coupons** at checkout (percent or flat discounts)
- **Wallet** — starting balance on signup, top-up anytime
- **Food Points** — earn 1 point per ₹10 spent
- **Seat reservations** — check live seat availability per restaurant and book a table
- **Order tracking** — see status (`Preparing → Confirmed → Ready → Delivered`)
- **Favorites** — save dishes you love for quick access
- **Reviews** — rate and review restaurants (1–5 stars)
- **Announcements/notifications** feed

### 👑 Admin side
- Manage users (view & delete accounts)
- Manage restaurants and seating (refill, set available/total seats)
- Manage food items (add, edit, delete, stock, pricing, categories)
- Manage orders (update status through the full lifecycle)
- Manage coupons (create, edit, delete)
- Manage reviews (moderate/delete)
- **Revenue dashboard** — total revenue, average order value, top-selling item, highest single order, status breakdown
- Activity log viewer (last 20 actions, also persisted to `log.json`)
- Send announcements to all users
- **Settings** — backup data on demand, list backups, restore from any backup

### 🎨 Terminal UI
- ANSI-colored output with a small design-system layer (`C` class, `header()`, `menu_box()`, `status_badge()`, `seat_bar()`, etc.)
- Automatically enables ANSI colors on Windows
- Boxed menus, progress-style seat availability bars, colored status badges

---

## 🗂️ Project structure

```
alakh_dhaaba.py          # the entire application
alakh_dhaaba_data.json   # auto-created on first run — all persistent data
log.json                 # auto-created — rolling activity log (last 250 entries)
backups/                 # created via Admin → Settings → Backup Data
```

Everything lives in **one file**, organized into clearly labeled sections:

| Section | What it does |
|---|---|
| Design System | ANSI colors, boxes, headers, badges |
| Data | Default seed data (users, restaurants, menus, coupons) |
| Basic Helpers | Load/save JSON, ID generation, password hashing, data migration/normalization |
| Food / Restaurants | Browsing, searching, menu display |
| Cart | Add/remove/update items, cart totals |
| Checkout / Orders | Coupon application, payment, order history |
| Seats / Reservations | Seat booking and availability |
| Favorites | Save/remove favorite dishes |
| Wallet | Balance top-up, food points |
| Reviews | Submit and view reviews |
| Profile | Edit name/password |
| Announcements | View notifications |
| User Portal | Main logged-in menu |
| Register / Login | Account creation and authentication |
| Admin Portal | Full back-office suite |
| Main | Entry point / top-level menu |

---

## ▶️ Getting started

**Requirements:** Python 3.7+ (standard library only — nothing to `pip install`)

```bash
python alakh_dhaaba.py
```

On first run, the app creates `alakh_dhaaba_data.json` pre-seeded with:
- 2 demo users (`prince` / `winkle`)
- 4 restaurants: Pizza Palace 🍕, Wok Express 🍜, Spice Hub 🍚, Burger Point 🍔
- ~24 menu items per restaurant, each with price, category, description, rating, and stock
- 2 starter coupons: `SAVE10` (10% off) and `FLAT50` (₹50 off)

### Demo logins
| Username | Password |
|---|---|
| `prince` | `2007` |
| `winkle` | `2711` |

### Admin login
| Username | Password |
|---|---|
| `admin` | `admin123` |



## 📄 License

Personal / educational project — adapt freely. 
