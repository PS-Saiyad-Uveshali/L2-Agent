"""LiteLLM Agent implementation for L2 Wizard."""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import AgentConfig
from tools import ToolRegistry


class LiteLLMAgent:
    """
    Production-ready agent using LiteLLM proxy with structured tool calling.
    
    This agent implements a clean agent loop pattern:
    1. Send user message + tool definitions to LiteLLM
    2. Model responds with either tool calls or final answer
    3. Execute tool calls and add results to conversation
    4. Loop until model provides final answer
    """
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        """
        Initialize the LiteLLM Agent.
        
        Args:
            api_key: DeepInfra API key (defaults to config)
            verbose: Whether to print step-by-step progress
        """
        self.api_key = api_key or AgentConfig.DEEPINFRA_API_KEY
        if not self.api_key:
            raise ValueError("DEEPINFRA_API_KEY is required")
        
        # Initialize OpenAI client pointing to LiteLLM proxy
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=AgentConfig.LITELLM_BASE_URL
        )
        self.verbose = verbose
        self.tool_registry = ToolRegistry()
        self.tool_definitions = self.tool_registry.get_tool_definitions_openai_format()
        
        # System prompt defines agent behavior
        self.system_prompt = """You are a helpful AI assistant that can help users with various tasks.
You have access to several tools for getting information:
- Weather information for any location
- Book recommendations by topic
- Random jokes for entertainment
- Random dog pictures
- Trivia questions

When a user asks for help, determine which tools are needed and call them.
Always provide friendly, conversational responses that incorporate the tool results naturally.
If coordinates are mentioned, use them for weather. Parse requests carefully to identify all needed tools."""
    
    def run(self, user_message: str, max_iterations: Optional[int] = None) -> str:
        """
        Run the agent loop for a single user message.
        
        Args:
            user_message: The user's input message
            max_iterations: Maximum number of agent loop iterations (defaults to config)
            
        Returns:
            Final agent response as a string
        """
        max_iterations = max_iterations or AgentConfig.MAX_ITERATIONS
        
        # Initialize conversation with system message and user message
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        if self.verbose:
            print(f"\n🤖 Processing: {user_message}\n")
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            if self.verbose:
                print(f"[Iteration {iteration}]")
            
            try:
                # Call LiteLLM with current conversation state
                response = self.client.chat.completions.create(
                    model=AgentConfig.MODEL_NAME,
                    max_tokens=AgentConfig.MAX_TOKENS,
                    temperature=AgentConfig.TEMPERATURE,
                    messages=messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # Check if model wants to use tools
                if message.tool_calls:
                    # Model wants to use tools
                    if self.verbose:
                        print(f"📋 Model requested {len(message.tool_calls)} tool call(s)")
                    
                    # Add assistant's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            } for tc in message.tool_calls
                        ]
                    })
                    
                    # Execute all requested tools
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        # Handle empty arguments for tools with no parameters
                        tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        
                        if self.verbose:
                            print(f"  → Calling {tool_name} with {tool_args}")
                        
                        # Execute tool
                        try:
                            result = self.tool_registry.execute_tool(tool_name, tool_args)
                            if self.verbose:
                                print(f"    ✓ Success")
                        except Exception as e:
                            result = {"error": str(e)}
                            if self.verbose:
                                print(f"    ✗ Error: {e}")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(result)
                        })
                    
                    if self.verbose:
                        print()
                
                else:
                    # Model provided final answer without tool use
                    final_text = message.content or ""
                    if self.verbose:
                        print("✓ Final answer provided\n")
                    return final_text
                    
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error in iteration {iteration}: {e}")
                raise
        
        # Max iterations reached
        if self.verbose:
            print(f"⚠ Max iterations ({max_iterations}) reached\n")
        return "I apologize, but I couldn't complete your request within the iteration limit."
    
    def interactive_mode(self):
        """Run the agent in interactive mode for testing."""
        print("=" * 60)
        print("L2 Wizard - LiteLLM Agent (Level 3)")
        print("=" * 60)
        print(f"\nUsing model: {AgentConfig.MODEL_NAME}")
        print(f"Via LiteLLM Proxy: {AgentConfig.LITELLM_BASE_URL}")
        print("\nAvailable capabilities:")
        print("  🌤️  Weather information (provide coordinates)")
        print("  📚 Book recommendations")
        print("  😄 Random jokes")
        print("  🐕 Dog pictures")
        print("  🎯 Trivia questions")
        print("\nType 'exit' or 'quit' to stop.\n")
        
        while True:
            try:
                user_input = input("🔷 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in {"exit", "quit", "q"}:
                    print("\n👋 Goodbye!\n")
                    break
                
                response = self.run(user_input)
                print(f"\n🎯 Agent: {response}\n")
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                if self.verbose:
                    import traceback
                    traceback.print_exc()


def main():
    """Main entry point for the agent."""
    try:
        # Validate configuration
        AgentConfig.validate()
        
        # Create and run agent
        agent = LiteLLMAgent(verbose=AgentConfig.VERBOSE)
        agent.interactive_mode()
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        print("Please set the DEEPINFRA_API_KEY environment variable:")
        print("  Windows PowerShell: $env:DEEPINFRA_API_KEY='your-key-here'")
        print("  Linux/Mac: export DEEPINFRA_API_KEY='your-key-here'")
        print("  Or add it to your .env file")
        print()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
