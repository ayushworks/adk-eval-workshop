"""Refund-support agent package.

ADK discovers the agent through this import: `adk web` and `adk eval` look for a
module that exposes `root_agent`.
"""

from . import agent
from .agent import root_agent

__all__ = ["agent", "root_agent"]
