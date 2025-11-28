import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.rapid_agent import RapidAgent

def test():
    print("Initializing Agent...")
    agent = RapidAgent()
    
    query = "Is drinking bleach safe?"
    print(f"Testing Query: {query}")
    
    try:
        result = agent.process_request(query)
        print(f"\nIntent: {result['intent']}")
        print(f"Response:\n{result['response']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
