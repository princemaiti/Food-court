"""
UI helpers for Alakh Da Dhaaba
"""

import os
import shutil
from typing import List, Tuple

class Colors:
    """ANSI color codes"""
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

# Enable ANSI on Windows
if os.name == "nt":
    os.system("")

C = Colors()

def get_width() -> int:
    """Get terminal width, capped for readability"""
    try:
        return min(shutil.get_terminal_size().columns, 64)
    except OSError:
        return 64

def clear_screen():
    """Clear terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")

def line(char: str = "─", color: str = C.GREY):
    """Print horizontal line"""
    print(f"{color}{char * get_width()}{C.RESET}")

def small_line():
    """Print small dotted line"""
    line("·", C.GREY)

def pause():
    """Pause for user input"""
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

def header(title: str, emoji: str = ""):
    """Print boxed header"""
    w = get_width()
    label = f" {emoji}  {title} " if emoji else f" {title} "
    print(f"{C.CYAN}{'═' * w}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}{label.center(w)}{C.RESET}")
    print(f"{C.CYAN}{'═' * w}{C.RESET}")

def sub_header(title: str, emoji: str = ""):
    """Print sub-header"""
    w = get_width()
    label = f"{emoji}  {title}" if emoji else title
    print(f"{C.MAGENTA}{label}{C.RESET}")
    print(f"{C.GREY}{'─' * min(len(label) + 4, w)}{C.RESET}")

def success(msg: str):
    """Print success message"""
    print(f"{C.GREEN}✅ {msg}{C.RESET}")

def error(msg: str):
    """Print error message"""
    print(f"{C.RED}❌ {msg}{C.RESET}")

def warn(msg: str):
    """Print warning message"""
    print(f"{C.YELLOW}⚠️  {msg}{C.RESET}")

def info(msg: str):
    """Print info message"""
    print(f"{C.BLUE}ℹ️  {msg}{C.RESET}")

def money(amount) -> str:
    """Format money with color"""
    return f"{C.GREEN}₹{amount}{C.RESET}"

def money_plain(amount) -> str:
    """Format money without color"""
    return f"₹{amount}"

def menu_box(options: List[Tuple[str, str]]):
    """Print numbered menu in a box"""
    w = get_width()
    print(f"{C.CYAN}┌{'─' * (w - 2)}┐{C.RESET}")
    for number, label in options:
        text = f" {C.YELLOW}{number}.{C.RESET} {label}"
        pad = w - 2 - len(f" {number}. {label}")
        print(f"{C.CYAN}│{C.RESET}{text}{' ' * max(pad, 0)}{C.CYAN}│{C.RESET}")
    print(f"{C.CYAN}└{'─' * (w - 2)}┘{C.RESET}")

def status_badge(status: str) -> str:
    """Get colored status badge"""
    colors = {
        "Preparing": C.YELLOW,
        "Confirmed": C.GREEN,
        "Ready": C.CYAN,
        "Delivered": C.GREEN,
        "Cancelled": C.RED,
    }
    color = colors.get(status, C.WHITE)
    return f"{color}{C.BOLD}{status}{C.RESET}"

def seat_bar(available: int, total: int, width: int = 20) -> str:
    """Visual bar showing seat occupancy"""
    if total <= 0:
        return ""
    filled = round((available / total) * width)
    filled = max(0, min(width, filled))
    bar = f"{C.GREEN}{'█' * filled}{C.GREY}{'░' * (width - filled)}{C.RESET}"
    return f"{bar} {C.WHITE}{available}/{total}{C.RESET}"

def rating_stars(rating: float) -> str:
    """Convert rating to star display"""
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars = "★" * full_stars
    if half_star:
        stars += "⯨"
    stars += "☆" * empty_stars
    return f"{C.YELLOW}{stars}{C.RESET}"