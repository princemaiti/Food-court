"""Admin portal navigation for the terminal application."""

from ui import C, clear_screen, header, menu_box, metric_cards, pause, success, small_line, status_badge


class AdminPortalMixin:
    """Navigation loop for administrator operations."""

    def admin_portal(self):
        """Run the admin portal until logout."""
        while True:
            clear_screen()
            header("ADMIN PORTAL", "👑")
            data = self.service.db.data
            print(f"{C.GREY}CONTROL CENTER  •  Secure administrator workspace{C.RESET}\n")
            metric_cards([
                ("USERS", str(len(data.get("users", {}))), C.CYAN),
                ("ORDERS", str(len(data.get("orders", []))), C.GREEN),
                ("BRANCHES", str(len(data.get("restaurants", {}))), C.ORANGE),
                ("REVIEWS", str(len(data.get("reviews", []))), C.YELLOW),
            ])
            print()
            menu_box([
                ("1", "👥 Manage Users"), ("2", "📦 Manage Orders"), ("3", "📊 Dashboard Stats"),
                ("4", "🏪 Manage Hotels / Food"), ("5", "⭐ Manage Reviews"),
                ("6", "🔔 Announcements"), ("7", "💾 Backup Data"),
                ("8", "📜 Activity Logs"), ("9", "🚪 Logout"),
            ])
            choice = input(f"\n{C.CYAN}Choose: {C.RESET}").strip()
            screens = {
                "1": self.admin_users_screen, "2": self.admin_orders_screen,
                "3": self.admin_stats_screen, "4": self.admin_restaurants_screen,
                "5": self.admin_reviews_screen, "6": self.admin_announcements_screen,
            }
            if choice in screens:
                screens[choice]()
            elif choice == "7":
                backup_path = self.service.db.backup()
                success(f"Backup created at: {backup_path}")
                pause()
            elif choice == "8":
                self.activity_logs_screen()
            elif choice == "9":
                return

    def activity_logs_screen(self):
        """Display the most recent activity entries."""
        clear_screen()
        header("ACTIVITY LOGS", "📜")
        print()
        logs = self.service.db.data.get("activity_logs", [])
        if not logs:
            print(f"{C.GREY}No activity recorded yet.{C.RESET}")
        else:
            for entry in reversed(logs[-20:]):
                print(f"{C.GREY}{entry.get('time', '')}{C.RESET} | {C.BOLD}{entry.get('username', 'system')}{C.RESET} | {entry.get('action', '')}")
                if entry.get("details"):
                    print(f"   {C.WHITE}{entry['details']}{C.RESET}")
                small_line()
        pause()