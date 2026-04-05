"""
測試：Navigation Agent
"""
import sys
sys.path.insert(0, 'src')

from agent.navigation_agent import NavigationAgent


def test_agent_analyze():
    agent = NavigationAgent()
    
    test_data = {
        "obstacles": [
            {"type": "pole", "distance": 2.0, "direction": "center"}
        ]
    }
    
    result = agent.analyze_environment(test_data)
    print(f"Result: {result}")
    assert result is not None


if __name__ == "__main__":
    test_agent_analyze()
    print("✅ NavigationAgent tests passed")
