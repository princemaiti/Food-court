"""Generate isolated JSON data to measure future-scale loading performance."""

import argparse
import json
import random
import time
from pathlib import Path


def build_dataset(users: int, restaurants: int, foods: int, orders: int, reviews: int) -> dict:
    """Build a synthetic dataset without touching the application's live data."""
    data = {"users": {}, "restaurants": {}, "orders": [], "reviews": []}
    for index in range(1, users + 1):
        data["users"][f"user_{index:06d}"] = {
            "user_id": f"user_{index:06d}", "name": f"Customer {index}",
            "wallet": random.randint(100, 20000), "orders": [], "favorites": [],
        }
    for index in range(1, restaurants + 1):
        restaurant_id = f"restaurant_{index:06d}"
        data["restaurants"][restaurant_id] = {
            "restaurant_id": restaurant_id, "name": f"Branch {index}",
            "menu": {
                f"food_{index:06d}_{item:03d}": {
                    "food_id": f"food_{index:06d}_{item:03d}",
                    "name": f"Menu Item {index}-{item}", "price": random.randint(30, 500),
                    "stock": random.randint(0, 100),
                }
                for item in range(1, max(1, foods // restaurants) + 1)
            },
        }
    restaurant_ids = list(data["restaurants"])
    for index in range(1, orders + 1):
        user_id = f"user_{random.randint(1, users):06d}"
        restaurant_id = random.choice(restaurant_ids)
        food_id, food = random.choice(list(data["restaurants"][restaurant_id]["menu"].items()))
        order_id = f"order_{index:06d}"
        data["orders"].append({
            "order_id": order_id, "user_id": user_id,
            "items": [{"food_id": food_id, "restaurant_id": restaurant_id, "quantity": 1, "price": food["price"]}],
            "total": food["price"], "status": random.choice(["Preparing", "Confirmed", "Delivered"]),
        })
        data["users"][user_id]["orders"].append(order_id)
    for index in range(1, reviews + 1):
        data["reviews"].append({
            "review_id": f"review_{index:06d}",
            "user_id": f"user_{random.randint(1, users):06d}",
            "restaurant_id": random.choice(restaurant_ids),
            "rating": random.randint(1, 5), "comment": "Synthetic performance review",
        })
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=10_000)
    parser.add_argument("--restaurants", type=int, default=1_000)
    parser.add_argument("--foods", type=int, default=50_000)
    parser.add_argument("--orders", type=int, default=100_000)
    parser.add_argument("--reviews", type=int, default=500_000)
    parser.add_argument("--output", type=Path, default=Path("data/stress_food_court.json"))
    args = parser.parse_args()
    started = time.perf_counter()
    dataset = build_dataset(args.users, args.restaurants, args.foods, args.orders, args.reviews)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, separators=(",", ":")), encoding="utf-8")
    elapsed = time.perf_counter() - started
    print(f"Generated {args.users} users, {args.restaurants} restaurants, {args.orders} orders, {args.reviews} reviews in {elapsed:.2f}s")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()