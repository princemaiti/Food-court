"""
UI helpers for Alakh Da Dhaaba
"""

import os
import re
import shutil
import unicodedata
from typing import Any, List, Tuple

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

def safe_icon(icon: str) -> str:
    """Keep the original emoji without adding a terminal background."""
    return icon

def _visible_length(text: str) -> int:
    """Return terminal display width without ANSI or zero-width emoji marks."""
    plain_text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    width = 0
    joined_emoji = False
    for index, character in enumerate(plain_text):
        if character == "\u200d":
            joined_emoji = True
            continue
        if joined_emoji:
            joined_emoji = False
            continue
        if (
            unicodedata.combining(character)
            or unicodedata.category(character) in {"Cf", "Mn", "Me"}
            or character in {"\ufe0e", "\ufe0f"}
        ):
            continue
        emoji_presentation = (
            index + 1 < len(plain_text)
            and plain_text[index + 1] == "\ufe0f"
            and 0x2000 <= ord(character) <= 0x32FF
        )
        width += 2 if emoji_presentation or unicodedata.east_asian_width(character) in {"W", "F"} else 1
    return width

def get_width() -> int:
    """Get terminal width, capped for readability"""
    try:
        return min(shutil.get_terminal_size().columns, 64)
    except OSError:
        return 64

def get_box_width() -> int:
    """Return a minimum width shared by all bordered components."""
    return max(get_width(), 32)

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
    w = get_box_width()
    label = f" {safe_icon(emoji)}  {title} " if emoji else f" {title} "
    print(f"{C.CYAN}{'═' * w}{C.RESET}")
    padding = max((w - _visible_length(label)) // 2, 0)
    print(f"{C.BOLD}{C.WHITE}{' ' * padding}{label}{C.RESET}")
    print(f"{C.CYAN}{'═' * w}{C.RESET}")

def sub_header(title: str, emoji: str = ""):
    """Print sub-header"""
    w = get_width()
    label = f"{emoji}  {title}" if emoji else title
    print(f"{C.MAGENTA}{label}{C.RESET}")
    print(f"{C.GREY}{'─' * min(_visible_length(label) + 4, w)}{C.RESET}")

def success(msg: str):
    """Print success message"""
    print(f"{C.GREEN}{safe_icon('✅')}  {msg}{C.RESET}")

def error(msg: str):
    """Print error message"""
    print(f"{C.RED}{safe_icon('❌')}  {msg}{C.RESET}")

def warn(msg: str):
    """Print warning message"""
    print(f"{C.YELLOW}{safe_icon('⚠️')}  {msg}{C.RESET}")

def info(msg: str):
    """Print info message"""
    print(f"{C.BLUE}{safe_icon('ℹ️')}  {msg}{C.RESET}")

def money(amount) -> str:
    """Format money with color"""
    return f"{C.GREEN}₹{amount}{C.RESET}"

def money_plain(amount) -> str:
    """Format money without color"""
    return f"₹{amount}"

def _menu_label(label: str) -> str:
    """Add consistent breathing room between an icon and its label."""
    label = label.strip()
    if not label or ord(label[0]) < 0x2000:
        return label
    separator = label.find(" ")
    if separator > 0:
        return f"{safe_icon(label[:separator])}  {label[separator + 1:].lstrip()}"
    return label

def menu_box(options: List[Tuple[str, str]]):
    """Print a consistently padded numbered menu in a box."""
    w = get_box_width()
    inner_width = w - 2
    print(f"{C.CYAN}┌{'─' * inner_width}┐{C.RESET}")
    for number, label in options:
        formatted_label = _menu_label(label)
        text = f" {C.YELLOW}{number}.{C.RESET} {formatted_label}"
        pad = inner_width - _visible_length(f" {number}. {formatted_label}")
        print(f"{C.CYAN}│{C.RESET}{text}{' ' * max(pad, 0)}{C.CYAN}│{C.RESET}")
    print(f"{C.CYAN}└{'─' * inner_width}┘{C.RESET}")

def pagination(items: List[Any], page: int, page_size: int = 10) -> Tuple[List[Any], int]:
    """Return one stable page of items and the total page count."""
    page_size = max(page_size, 1)
    total_pages = max((len(items) + page_size - 1) // page_size, 1)
    page = max(0, min(page, total_pages - 1))
    start = page * page_size
    return items[start:start + page_size], total_pages

def pagination_footer(page: int, total_pages: int, item_count: int) -> None:
    """Render compact navigation help for long lists."""
    print(
        f"\n{C.DIM}Showing page {page + 1}/{total_pages}  •  {item_count} items  •  "
        f"n next  p previous  0 back{C.RESET}"
    )

def food_card(number: str, name: str, price: str, restaurant: str, details: str, color: str = C.YELLOW) -> None:
    """Render a compact, aligned food item row."""
    print(f"{color}{number:>3}.{C.RESET} {C.BOLD}{name}{C.RESET}  {price}")
    print(f"     {C.GREY}{restaurant}  |  {details}{C.RESET}")

def restaurant_card(number: int, name: str, emoji: str, cuisine: str, hours: str,
                    service_style: str, seats: str, description: str = "") -> None:
    """Render a complete, aligned restaurant summary card."""
    width = get_box_width()
    inner_width = width - 4
    title = f"{number}. {safe_icon(emoji)}  {name}"
    print(f"{C.CYAN}┌{'─' * (width - 2)}┐{C.RESET}")
    _card_row(title, C.CYAN, C.BOLD + C.WHITE)
    _card_row(f"{cuisine}  |  {service_style}", C.CYAN, C.GREY)
    _card_row(f"Open {hours}  |  Seats {seats}", C.CYAN, C.GREY)
    if description:
        _card_row(description[:inner_width - 1], C.CYAN, C.WHITE)
    print(f"{C.CYAN}└{'─' * (width - 2)}┘{C.RESET}")

def announcement_card(number: int, message: str) -> None:
    """Render an announcement as a readable notification card."""
    panel(f"📢  UPDATE {number:02d}", [message], C.YELLOW)

def _card_row(text: str, border_color: str, text_color: str = "") -> None:
    """Render one fixed-width row shared by bordered cards."""
    width = get_box_width()
    available = width - 4
    text = str(text)
    if _visible_length(text) > available:
        text = text[:available - 1] + "…"
    padding = max(available - _visible_length(text), 0)
    print(f"{border_color}│{C.RESET} {text_color}{text}{C.RESET}{' ' * padding} {border_color}│{C.RESET}")

def panel(title: str, rows: List[str], color: str = C.CYAN):
    """Print a bordered information panel"""
    width = get_box_width()
    title = _menu_label(title)
    print(f"{color}┌─ {title} {'─' * max(width - _visible_length(title) - 5, 0)}┐{C.RESET}")
    for row in rows:
        _card_row(str(row), color)
    print(f"{color}└{'─' * (width - 2)}┘{C.RESET}")

def metric_cards(metrics: List[Tuple[str, str, str]]):
    """Print compact two-column metric cards"""
    width = get_width()
    if width < 52:
        for label, value, color in metrics:
            panel(label, [f"{color}{C.BOLD}{value}{C.RESET}"], color)
        return

    card_width = max((width - 6) // 2, 20)
    for index in range(0, len(metrics), 2):
        pair = metrics[index:index + 2]
        cards = []
        for label, value, color in pair:
            label_text = label[:card_width - 4]
            value_text = str(value)[:card_width - 4]
            cards.append(
                f"{C.GREY}{label_text}{C.RESET}\n"
                f"{color}{C.BOLD}{value_text}{C.RESET}"
            )
        while len(cards) < 2:
            cards.append("")
        print(f"{C.CYAN}┌{'─' * card_width}┐  ┌{'─' * card_width}┐{C.RESET}")
        left_lines = cards[0].splitlines() or [""]
        right_lines = cards[1].splitlines() or [""]
        for line_index in range(2):
            left = left_lines[line_index] if line_index < len(left_lines) else ""
            right = right_lines[line_index] if line_index < len(right_lines) else ""
            left_length = _visible_length(left_lines[line_index]) if line_index < len(left_lines) else 0
            right_length = _visible_length(right_lines[line_index]) if line_index < len(right_lines) else 0
            print(
                f"{C.CYAN}│{C.RESET} {left}{' ' * max(card_width - 1 - left_length, 0)}{C.CYAN}│{C.RESET}  "
                f"{C.CYAN}│{C.RESET} {right}{' ' * max(card_width - 1 - right_length, 0)}{C.CYAN}│{C.RESET}"
            )
        print(f"{C.CYAN}└{'─' * card_width}┘  └{'─' * card_width}┘{C.RESET}")

def progress_bar(value: float, maximum: float, width: int = 24, color: str = C.GREEN) -> str:
    """Render a compact proportional progress bar"""
    if maximum <= 0:
        ratio = 0
    else:
        ratio = max(0, min(1, value / maximum))
    filled = round(ratio * width)
    return f"{color}{'━' * filled}{C.GREY}{'─' * (width - filled)}{C.RESET}"

def status_badge(status: str) -> str:
    """Get a colored, easy-to-scan status badge."""
    colors = {
        "Preparing": C.YELLOW,
        "Confirmed": C.GREEN,
        "Ready": C.CYAN,
        "Delivered": C.GREEN,
        "Cancelled": C.RED,
    }
    color = colors.get(status, C.WHITE)
    return f"{color}{C.BOLD}● {status}{C.RESET}"

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