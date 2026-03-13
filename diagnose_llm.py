import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path so we can import 'mantriq'
sys.path.append(os.getcwd())

from mantriq.core.llm_engine import get_engine

load_dotenv()

def test_backend():
    print("--- MANTRIQ BACKEND DIAGNOSTICS ---")
    
    backend = os.getenv("MANTRIQ_BACKEND", "local")
    model = os.getenv("MANTRIQ_MODEL", "Not specified")
    
    print(f"Testing Backend: {backend}")
    print(f"Model Name: {model}")
    
    try:
        engine = get_engine()
        print(f"Successfully initialized {engine.backend} engine.")
        
        test_code = "def hello(): print('world')"
        print("\nInvoking test analysis (Explain Agent)...")
        
        # We invoke the engine directly to see where it fails
        response = engine.run_agent("Explain", test_code)
        
        print("\n--- RESPONSE RECEIVED ---")
        print(response)
        print("--------------------------")
        print("\nSuccess! The LLM is responding correctly.")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        print("\nFull Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_backend()
