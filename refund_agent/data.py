"""Seed data for the refund-support agent.

This is a deliberately tiny, in-memory "database". Everything is deterministic
so that evaluations are reproducible — the #1 rule of testable agents is that the
tools must not introduce randomness or hit live services.

The five orders are hand-picked to exercise every branch the agent can take:

    A1001  valid, within the refund window        -> refund SHOULD be issued
    A1002  valid, but PAST the refund window       -> refund must be DECLINED
    A1003  valid, item arrived damaged             -> refund SHOULD be issued
    A1004  (does not exist)                         -> agent must ask for a valid id
    A1005  valid, but ALREADY refunded             -> agent must NOT double-refund

"today" is pinned so the "within window" math never drifts between runs.
"""

from datetime import date

# Pinned reference date so policy-window math is deterministic across runs.
TODAY = date(2026, 6, 18)

# Refund policy per product category: how many days after the order date a
# refund can still be issued, plus any always-eligible conditions.
REFUND_POLICY = {
    "electronics": {
        "window_days": 30,
        "always_eligible_if": ["damaged", "defective"],
        "notes": "Electronics are refundable within 30 days, or any time if damaged or defective.",
    },
    "clothing": {
        "window_days": 60,
        "always_eligible_if": ["damaged"],
        "notes": "Clothing is refundable within 60 days, or any time if it arrived damaged.",
    },
    "default": {
        "window_days": 30,
        "always_eligible_if": ["damaged", "defective"],
        "notes": "Standard policy: refundable within 30 days, or any time if damaged or defective.",
    },
}

# The "orders" table. order_date is an ISO string; the tool layer parses it.
ORDERS = {
    "A1001": {
        "order_id": "A1001",
        "item": "Wireless headphones",
        "category": "electronics",
        "price": 79.99,
        "order_date": "2026-06-05",  # 13 days ago -> within 30-day window
        "status": "delivered",
        "refunded": False,
    },
    "A1002": {
        "order_id": "A1002",
        "item": "Bluetooth speaker",
        "category": "electronics",
        "price": 49.99,
        "order_date": "2026-04-01",  # 78 days ago -> OUTSIDE 30-day window
        "status": "delivered",
        "refunded": False,
    },
    "A1003": {
        "order_id": "A1003",
        "item": "Ceramic vase",
        "category": "home",
        "price": 49.99,
        "order_date": "2026-06-10",  # within window AND will be reported damaged
        "status": "delivered",
        "refunded": False,
    },
    "A1005": {
        "order_id": "A1005",
        "item": "Running shoes",
        "category": "clothing",
        "price": 119.99,
        "order_date": "2026-05-20",  # within window, but ALREADY refunded
        "status": "delivered",
        "refunded": True,
    },
    # NOTE: A1004 is intentionally absent so we can test the "order not found" path.
}
