# 🍽️ ALAKH DA DHAABA

A terminal-based food-court management system built with Python's standard library.
It is designed as a learning project: it demonstrates authentication, carts, wallets,
orders, reservations, reviews, administration, backups, and JSON persistence.

## Requirements
Money is represented as whole Indian rupees using integer arithmetic. This avoids floating-
point rounding in the current product model; paise and payment-provider integration are
outside the scope of this project.

## Architecture

The active application follows a small layered CLI architecture:

```text
main.py       presentation, input handling, navigation
services.py   business workflows and validation
models.py     domain objects and invariants
database.py   JSON persistence, backups, and activity logs
ui.py         terminal rendering helpers
config.py     paths and application constants
tests/        standard-library regression tests
```

The CLI calls services for state changes. Services update models and persistence; UI
helpers only render output. The project intentionally keeps JSON and the terminal UI
because they are appropriate for this educational scope. Further growth should split
`main.py` and `services.py` by feature, starting with authentication, orders, restaurants,
and administration, while preserving these boundaries.

## Known Scope Limits

- JSON persistence has no database transactions or multi-process concurrency control.
- Backups should be created before manual data editing or experimental changes.
- Admin credentials should be moved to an environment variable or secret store before
	deploying beyond a local classroom/demo environment.

**License:** MIT

---

## ✨ FEATURES

### 👤 User Features
- **User Authentication** - Secure registration & login with SHA-256 password hashing
- **Browse Restaurants** - 4 restaurants with 40+ food items
- **Smart Cart System** - Add/remove items, change quantities, real-time total
- **Wallet System** - Add money, track balance, earn food points
- **Seat Reservation** - Book seats at restaurants with visual occupancy bars
- **Order Management** - Place orders, track status, cancel with refund
- **Favorites** - Save favorite food items for quick access
- **Reviews & Ratings** - Rate restaurants and write reviews
- **Coupon System** - Apply discount codes during checkout
- **Receipt Generation** - Automatic text receipts for every order

### 👑 Admin Features
- **Dashboard** - View users, orders, revenue statistics
- **Manage Restaurants** - Reset seats, view occupancy
- **Order Management** - Update order statuses (Preparing → Confirmed → Ready → Delivered)
- **Announcements** - Send notifications to all users
- **Activity Logs** - Track all system activities
- **Data Backup** - Create timestamped backups

### 🎨 UI Features
- **ANSI Colors** - Beautiful colored terminal interface
- **Box Drawing** - Professional menus with borders
- **Seat Visualization** - Visual bars showing seat occupancy
- **Status Badges** - Color-coded order statuses
- **Cross-Platform** - Works on Windows, Linux, and macOS

---

## 🚀 QUICK START

### Prerequisites
- Python 3.8 or higher
- No external dependencies required! (Uses only standard library)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/princemaiti/food-court.git
cd food-court