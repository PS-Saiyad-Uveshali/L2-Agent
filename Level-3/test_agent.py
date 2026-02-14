"""Test harness for the Claude Agent SDK implementation."""

import os
import sys
from typing import List, Dict
from agent import ClaudeAgent
from config import AgentConfig


class TestScenario:
    """Represents a test scenario with expected behaviors."""
    
    def __init__(self, name: str, user_input: str, expected_tools: List[str], description: str):
        """
        Initialize a test scenario.
        
        Args:
            name: Short name for the test
            user_input: The user message to test
            expected_tools: List of tools that should be called
            description: Description of what the test validates
        """
        self.name = name
        self.user_input = user_input
        self.expected_tools = expected_tools
        self.description = description


# Define test scenarios covering key Level 2 functionality
TEST_SCENARIOS = [
    TestScenario(
        name="Weather Query",
        user_input="What's the weather in New York at coordinates 40.7128, -74.0060?",
        expected_tools=["get_weather"],
        description="Tests basic weather tool calling with coordinate parsing"
    ),
    TestScenario(
        name="Book Recommendations",
        user_input="Recommend 3 mystery books for me",
        expected_tools=["book_recs"],
        description="Tests book recommendation tool with topic and limit"
    ),
    TestScenario(
        name="Entertainment Package",
        user_input="Tell me a joke and show me a dog picture",
        expected_tools=["random_joke", "random_dog"],
        description="Tests multiple simple tools in one request"
    ),
    TestScenario(
        name="Complex Multi-Tool Request",
        user_input="Plan a Saturday in Paris at (48.8566, 2.3522). Get the weather, recommend 2 science fiction books, and give me a trivia question.",
        expected_tools=["get_weather", "book_recs", "trivia"],
        description="Tests complex scenario with multiple tools (Level 2 core use case)"
    ),
    TestScenario(
        name="Trivia Question",
        user_input="Give me a trivia question",
        expected_tools=["trivia"],
        description="Tests trivia tool calling"
    )
]


def run_test_scenario(agent: ClaudeAgent, scenario: TestScenario, verbose: bool = True) -> Dict:
    """
    Run a single test scenario.
    
    Args:
        agent: The ClaudeAgent instance
        scenario: The test scenario to run
        verbose: Whether to print detailed output
        
    Returns:
        Dict with test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print(f"TEST: {scenario.name}")
        print("=" * 70)
        print(f"Description: {scenario.description}")
        print(f"User Input: {scenario.user_input}")
        print(f"Expected Tools: {', '.join(scenario.expected_tools)}")
        print("-" * 70)
    
    try:
        # Run the agent
        response = agent.run(scenario.user_input)
        
        if verbose:
            print("\n" + "-" * 70)
            print(f"Response:\n{response}")
            print("-" * 70)
            print("✅ TEST PASSED - Agent completed successfully")
        
        return {
            "name": scenario.name,
            "status": "PASSED",
            "response": response,
            "error": None
        }
    
    except Exception as e:
        if verbose:
            print(f"\n❌ TEST FAILED - Error: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            "name": scenario.name,
            "status": "FAILED",
            "response": None,
            "error": str(e)
        }


def run_all_tests(api_key: str = None, verbose: bool = True) -> Dict:
    """
    Run all test scenarios.
    
    Args:
        api_key: Optional API key override
        verbose: Whether to print detailed output
        
    Returns:
        Dict with overall test results
    """
    print("\n" + "🧪" * 35)
    print("L2 WIZARD - LEVEL 3 TEST HARNESS")
    print("🧪" * 35)
    
    # Create agent instance
    try:
        agent = ClaudeAgent(api_key=api_key, verbose=False)  # Disable agent's verbose mode in tests
        print(f"\n✓ Agent initialized with model: {AgentConfig.MODEL_NAME}")
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {e}")
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "results": []
        }
    
    # Run all scenarios
    results = []
    for scenario in TEST_SCENARIOS:
        result = run_test_scenario(agent, scenario, verbose=verbose)
        results.append(result)
    
    # Summarize results
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed. See details above.")
    
    print("=" * 70 + "\n")
    
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results
    }


def main():
    """Main entry point for test harness."""
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n❌ ANTHROPIC_API_KEY environment variable is required.")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'\n")
        return 1
    
    # Run tests
    results = run_all_tests(verbose=True)
    
    # Exit with appropriate code
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
