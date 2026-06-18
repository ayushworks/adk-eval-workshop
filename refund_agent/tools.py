"""The three tools the refund agent can call.

Design notes for the workshop:

* All three are plain Python functions wrapped as ADK FunctionTools. They are
  deterministic and side-effect-free against an in-memory dict, which is what
  makes the agent reproducibly evaluable.

* There are exactly three because that is the smallest set that makes
  *trajectory* evaluation interesting:
      get_order_status  (read)   -> find the order, can fail
      get_refund_policy (read)   -> the eligibility check
      issue_refund      (write)  -> the risky action, must come last & only if eligible

  The "correct" trajectory is: look up the order -> check the policy ->
  (only if eligible) issue the refund. Refunding before checking the policy is
  the dangerous shortcut the trajectory eval is designed to catch.
"""

from datetime import date

from google.adk.tools import FunctionTool

from .data import ORDERS, REFUND_POLICY, TODAY


def get_order_status(order_id: str) -> dict:
    """Look up an order by its ID.

    Args:
        order_id: The customer's order identifier, e.g. "A1001".

    Returns:
        A dict describing the order. If the order does not exist, returns
        {"found": False, ...} so the agent can ask for a valid ID instead of
        guessing.
    """
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {
            "found": False,
            "order_id": order_id,
            "message": f"No order found with ID '{order_id}'.",
        }
    return {
        "found": True,
        "order_id": order["order_id"],
        "item": order["item"],
        "category": order["category"],
        "price": order["price"],
        "order_date": order["order_date"],
        "status": order["status"],
        "already_refunded": order["refunded"],
    }


def get_refund_policy(category: str) -> dict:
    """Return the refund policy for a product category.

    Args:
        category: The product category, e.g. "electronics" or "clothing".
            Unknown categories fall back to the default policy.

    Returns:
        A dict with the refund window in days, the conditions that make an item
        always eligible (e.g. "damaged"), and a human-readable note.
    """
    policy = REFUND_POLICY.get(category.strip().lower(), REFUND_POLICY["default"])
    return {
        "category": category,
        "window_days": policy["window_days"],
        "always_eligible_if": policy["always_eligible_if"],
        "notes": policy["notes"],
    }


def issue_refund(order_id: str, amount: float) -> dict:
    """Issue a refund for an order. THIS IS THE WRITE ACTION.

    Only call this after confirming, via get_order_status and get_refund_policy,
    that the order exists, has not already been refunded, and is eligible under
    policy. Never refund more than the order's price.

    Args:
        order_id: The order to refund, e.g. "A1001".
        amount: The amount to refund in dollars. Must not exceed the price paid.

    Returns:
        A dict confirming the refund, or an error describing why it was refused.
    """
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"success": False, "error": f"No order found with ID '{order_id}'."}
    if order["refunded"]:
        return {
            "success": False,
            "error": f"Order {order['order_id']} has already been refunded. Not issuing a second refund.",
        }
    if amount > order["price"]:
        amount_str = format(amount, ".2f")
        price_str = format(order["price"], ".2f")
        return {
            "success": False,
            "error": (
                "Refund amount of USD " + amount_str
                + " exceeds the order price of USD " + price_str + "."
            ),
        }
    # In a real system this would write to a ledger. Here we just confirm.
    amount_str = format(round(amount, 2), ".2f")
    return {
        "success": True,
        "order_id": order["order_id"],
        "refund_amount": round(amount, 2),
        "eta_business_days": "5-7",
        "message": "Refund of USD " + amount_str + " approved for order " + order["order_id"] + ".",
    }


# Wrap the plain functions as ADK tools.
get_order_status_tool = FunctionTool(func=get_order_status)
get_refund_policy_tool = FunctionTool(func=get_refund_policy)
issue_refund_tool = FunctionTool(func=issue_refund)

ALL_TOOLS = [get_order_status_tool, get_refund_policy_tool, issue_refund_tool]
