from .explain_agent import ExplainAgent
from .debug_agent import DebugAgent
from .review_agent import ReviewAgent
from .optimize_agent import OptimizeAgent
from .chat_agent import ChatAgent

AGENT_MAP = {
    "Chat": ChatAgent,
    "Explain": ExplainAgent,
    "Debug": DebugAgent,
    "Review": ReviewAgent,
    "Optimize": OptimizeAgent
}
