from mantriq.core.llm_engine import get_engine

class DebugAgent:
    def __init__(self):
        self.engine = get_engine()

    def process(self, code: str) -> str:
        return self.engine.run_agent("Debug", code)
