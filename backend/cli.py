import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.rapid_agent import RapidAgent

def main():
    print("=== PerspectAI Rapid Layer (Phase 1) ===")
    print("Initializing Agent...")
    agent = RapidAgent()
    print("Agent Ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        if not user_input.strip():
            continue

        print("Thinking...", end="", flush=True)
        try:
            result = agent.process_request(user_input)
            print(f"\r[Intent: {result['intent']}]")
            print(f"PerspectAI: {result['response']}")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
