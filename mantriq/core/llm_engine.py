import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from mantriq.core.prompts import get_prompt_template

# Load environment variables from .env file
load_dotenv()

class LLMEngine:
    def __init__(self, backend: str = "ollama", model: str = None):
        self.backend = os.getenv("MANTRIQ_BACKEND", backend).lower()
        self.model_name = os.getenv("MANTRIQ_MODEL", model)
        self.init_error = None
        try:
            self.llm = self._initialize_llm()
        except Exception as e:
            self.init_error = str(e)
            # Fallback to mock backend if initialization fails
            print(f"\n[ERROR] Backend Initialization Failed: {self.init_error}")
            print("[INFO] Falling back to 'mock' mode. AI responses will be simulated.")
            print("[INFO] Please run 'npm run install-standalone' if you intended to use the 'local' backend.\n")
            self.backend = "mock"
            self.llm = MockLLM()

    def _initialize_llm(self):
        if self.backend == "ollama":
            from langchain_ollama import OllamaLLM
            model = self.model_name or "llama2"
            return OllamaLLM(model=model)
        
        elif self.backend == "local":
            return LocalLLM(model_name=self.model_name)
        
        elif self.backend == "openai":
            from langchain_openai import ChatOpenAI
            model = self.model_name or "gpt-4o"
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment or .env file.")
            return ChatOpenAI(model=model, api_key=api_key)
        
        elif self.backend == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = self.model_name or "gemini-1.5-pro"
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment or .env file.")
            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        
        elif self.backend == "mock":
            return MockLLM()
        
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def run_agent(self, agent_name: str, code: str) -> str:
        try:
            prompt_template = get_prompt_template(agent_name)
            
            # For ChatModels (OpenAI/Gemini), we should use a human message if the template doesn't handle it
            # But PromptTemplate.from_template is usually fine with invoke.
            # Let's ensure the backend is initialized correctly
            
            chain = prompt_template | self.llm | StrOutputParser()
            
            # Add a timeout to avoid hanging indefinitely
            response = chain.invoke({"code": code})
            
            if not response:
                return "The AI returned an empty response. Please try again or check your backend settings."
            
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG: LLM Invocation Error:\n{error_details}")
            
            error_msg = str(e).lower()
            if self.backend == "ollama":
                if "connection refused" in error_msg or "failed to connect" in error_msg:
                    raise ConnectionError("Could not connect to Ollama. Is it running? (Try 'ollama serve')")
                
                # Check for model not found error
                if "not found" in error_msg:
                    model_requested = self.model_name or "llama3"
                    raise ValueError(f"Model '{model_requested}' not found. Try 'ollama pull {model_requested}'")
            
            raise RuntimeError(f"Error using {self.backend} backend: {str(e)}")

from langchain_core.runnables import RunnableSerializable
from typing import Any, Dict, Optional, List

class LocalLLM(RunnableSerializable[Dict, str]):
    """Standalone local LLM using llama-cpp-python."""
    model_path: str = ""
    repo_id: str = "Qwen/Qwen2-0.5B-Instruct-GGUF"
    filename: str = "qwen2-0_5b-instruct-q8_0.gguf"
    _llm: Any = None

    def __init__(self, model_name=None, **kwargs):
        super().__init__(**kwargs)
        try:
            from llama_cpp import Llama
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError("Please run 'npm run install-standalone' to install required standalone dependencies (llama-cpp-python, huggingface_hub).")

        # Determine local path
        home = os.path.expanduser("~")
        model_dir = os.path.join(home, ".mantriq", "models")
        os.makedirs(model_dir, exist_ok=True)
        self.model_path = os.path.join(model_dir, self.filename)

        # Download if not present
        if not os.path.exists(self.model_path):
            print(f"\n[INFO] Standalone mode: Downloading tiny model (~500MB) to {self.model_path}...")
            print("[INFO] This only happens once.")
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                local_dir=model_dir
            )

        # Initialize the model with optimized context window
        self._llm = Llama(
            model_path=self.model_path,
            n_ctx=32768, # Match the model's training context
            n_threads=os.cpu_count(),
            verbose=False
        )

    def invoke(self, input_data: Any, config: Optional[Any] = None, **kwargs: Any) -> str:
        # Format input for the model
        prompt_str = ""
        
        # input_data might be a PromptValue or a dict
        if hasattr(input_data, "to_string"):
            prompt_str = input_data.to_string()
        elif isinstance(input_data, dict):
            # If it's a dict, we expect 'code' or similar keys from the template
            # However, prompt_template | llm passes the formatted prompt string/value
            prompt_str = str(input_data)
        else:
            prompt_str = str(input_data)
        
        # Remove any lingering "code='...'" wrapper if it's a raw dict string
        if prompt_str.startswith("{") and "code" in prompt_str:
             # This is a fallback for when the prompt isn't fully formatted
             import re
             match = re.search(r"'code':\s*'(.*?)'", prompt_str, re.DOTALL)
             if match:
                 prompt_str = match.group(1)

        # Simple instruction format for Qwen2
        formatted_prompt = f"<|im_start|>system\nYou are a helpful AI coding assistant.<|im_end|>\n<|im_start|>user\n{prompt_str}<|im_end|>\n<|im_start|>assistant\n"
        
        response = self._llm(
            formatted_prompt,
            max_tokens=1024,
            stop=["<|im_end|>"],
            echo=False
        )
        
        return response['choices'][0]['text'].strip()

class MockLLM:
    """A mock LLM for testing purposes without needing a real model."""
    def invoke(self, input_data):
        return f"MANTRIQ MOCK RESPONSE\nThis is a mock response for the provided code context.\nCode length: {len(input_data.get('code', ''))} characters."
    
    def __or__(self, other):
        # Support LCEL piping
        return MockChain(self, other)

class MockChain:
    def __init__(self, llm, parser):
        self.llm = llm
        self.parser = parser
    def invoke(self, input_data):
        return self.llm.invoke(input_data)

# Singleton instance
engine = None

def get_engine(backend: str = "ollama", model: str = None) -> LLMEngine:
    global engine
    if engine is None:
        engine = LLMEngine(backend=backend, model=model)
    return engine
