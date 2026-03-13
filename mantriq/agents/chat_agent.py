from mantriq.core.llm_engine import get_engine

class ChatAgent:
    def __init__(self):
        self.engine = get_engine()

    def process(self, query: str) -> str:
        return self.engine.run_agent("Chat", query)
