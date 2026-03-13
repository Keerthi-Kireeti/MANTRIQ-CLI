from .explain_agent import ExplainAgent
from .debug_agent import DebugAgent
from .review_agent import ReviewAgent
from .optimize_agent import OptimizeAgent

AGENT_MAP = {
    "Explain": ExplainAgent,
    "Debug": DebugAgent,
    "Review": ReviewAgent,
    "Optimize": OptimizeAgent
}
