"""
Configuration settings for Alakh Da Dhaaba
"""

import os

# File paths
DATA_FILE = "data/food_court.json"
LOG_FILE = "data/log.json"
BACKUP_DIR = "backups"
RECEIPT_DIR = "receipts"

# Admin credentials
ADMIN_USERNAME = os.getenv("FOODCOURT_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("FOODCOURT_ADMIN_PASSWORD", "admin123")

# Default wallet amounts
NEW_USER_WALLET = 500
DEFAULT_USER_WALLET = 1000

# Points system
POINTS_PER_RUPEE = 10  # 1 point for every ₹10 spent

# System settings
TERMINAL_WIDTH = 64
MAX_LOG_ENTRIES = 200