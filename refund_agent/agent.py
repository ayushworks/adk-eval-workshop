"""The refund-support agent.

This is the single agent we evaluate three ways during the workshop:
  1. trajectory  — did it call the right tools in the right order?
  2. judge       — was the final reply to the customer actually good?
  3. CI          — do both of the above run on every commit?

Read this file top to bottom in the walkthrough. The interesting design choices
are in the `instruction` — that is the contract the eval will hold the agent to.
"""

import os

from google.adk.agents import Agent
from google.genai import types

from .tools import ALL_TOOLS

# Model is read from the environment so the keys handed out at the workshop can
# point at whatever model the room is using. Falls back to a fast Gemini model.
MODEL = os.environ.get("WORKSHOP_MODEL", "gemini-3.1-flash-lite")

INSTRUCTION = """\
You are a customer-support agent for an online store. You handle refund requests.

Follow this procedure for EVERY refund request, in this exact order:

1. Identify the order. Call `get_order_status` with the order ID.
   - If the order is not found, do NOT guess. Ask the customer to double-check
     their order ID. Do not call any other tool.
   - If the order has already been refunded, tell the customer and do NOT issue
     another refund.

2. Check eligibility. Call `get_refund_policy` for the order's category BEFORE
   issuing any refund. An item is eligible if either:
     - it is within the policy's refund window (today minus the order date is
       less than or equal to window_days), OR
     - the customer says it arrived damaged or defective and that condition is
       in the policy's "always_eligible_if" list.
   - If the item is NOT eligible, politely decline and explain why. Do NOT call
     `issue_refund`.

3. Issue the refund. Only if the order exists, has not been refunded, and is
   eligible, call `issue_refund` with the order ID and the price paid. Never
   refund more than the price.

When you reply to the customer, always:
  - state the refund amount and the expected timeline if a refund was issued,
  - give a clear, specific reason for the decision,
  - keep a warm, professional tone,
  - never invent policy details that the tools did not return.

Today's date is 2026-06-18.
"""

root_agent = Agent(
    name="refund_agent",
    model=MODEL,
    description="Handles customer refund requests for an online store.",
    instruction=INSTRUCTION,
    tools=ALL_TOOLS,
    # temperature=0 makes tool-calling as deterministic as possible, which is
    # what you want for reproducible evals. Flaky evals usually trace back to a
    # non-zero temperature.
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)
