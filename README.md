# Alakh Da Dhaaba 🍽️

Alakh Da Dhaaba is a terminal-based food-court management system made with Python.

You can browse restaurants, order food, reserve seats, use coupons, manage your wallet,
save favourites, write reviews, and view your order history. An admin can manage users,
restaurants, menus, orders, announcements, backups, and statistics.

This is a learning project built with Python's standard library, so no extra packages are
needed.

## What You Can Do

### As a customer

- Create an account and log in
- Browse 8 restaurants and 160 food items
- Add food to your cart and place orders
- Pay using your wallet
- Use one-time coupons
- Reserve restaurant seats
- Cancel eligible orders and receive refunds
- Save favourite food items
- Review restaurants after ordering
- View notifications, receipts, points, and order history

### As an admin

- View dashboard statistics
- Manage customer accounts
- Make audited wallet adjustments
- Manage restaurants and menu items
- Update active order quantities and statuses
- View and remove reviews
- Publish announcements
- Create data backups
- View activity logs

## How to Run

You need Python 3.8 or newer.

Run the application:

```bash
py main.py
```

Run the tests:

```bash
py -m unittest discover -s tests -v
```

## Test Accounts

These accounts are already available:

| Username | Password |
| --- | --- |
| `prince` | `2007` |
| `winkle` | `2711` |
| `riya_sharma` | `demo1234` |
| `arjun_mehta` | `demo1234` |
| `neha_kapoor` | `demo1234` |
| `kabir_singh` | `demo1234` |

Admin login:

```text
Username: admin
Password: admin123
```

For local use, custom admin credentials can be set in PowerShell:

```powershell
$env:FOODCOURT_ADMIN_USERNAME = "your_admin"
$env:FOODCOURT_ADMIN_PASSWORD = "your_password"
py main.py
```

## Coupon Codes

- `SAVE10` - 10% off
- `FLAT50` - ₹50 off
- `WELCOME20` - 20% off your first order
- `FEAST100` - ₹100 off orders above ₹700
- `WEEKEND15` - 15% off

Each coupon can be used once per customer.

## Project Files

- `main.py` - Starts the application and contains screens
- `user_portal.py` - Customer navigation
- `admin_portal.py` - Admin navigation
- `services.py` - Main business logic
- `auth_service.py` - Login and registration logic
- `order_service.py` - Orders, refunds, and receipts
- `models.py` - User, food, cart, order, and reservation models
- `database.py` - JSON storage, backups, and data migration
- `ui.py` - Terminal colors, menus, cards, and layout
- `tests/` - Automated tests

## Data Storage

The application stores its data in `data/food_court.json`.

Backups are stored in `backups/`, and order receipts are stored in `receipts/`.
The project uses JSON because it is simple to understand and useful for learning.

## Large Data Testing

The project includes a separate stress-data generator. It creates synthetic data without
changing the live application database:

```bash
py stress_test.py
```

You can customize the number of users, restaurants, foods, orders, and reviews using the
available command-line options.

## License

MIT

# 🚀 QUICK START
Prerequisites
Python 3.8 or higher
No external dependencies required! (Uses only standard library)
Installation

Clone the repository

`git clone https://github.com/princemaiti/food-court.git`

cd food-court

