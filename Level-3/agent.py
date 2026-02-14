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
            base_url=AgentConfig.LITELLM_BASE_URL,
            timeout=120.0,  # 2 minutes timeout for slow proxies/models
            max_retries=2   # Retry failed requests twice
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
    
    def run(self, user_message: str, max_iterations: Optional[int] = None, stream: bool = False):
        """
        Run the agent loop for a single user message.
        
        Args:
            user_message: The user's input message
            max_iterations: Maximum number of agent loop iterations (defaults to config)
            stream: If True, yields response chunks as they arrive (generator)
            
        Returns:
            Final agent response as a string (or generator if stream=True)
        """
        if stream:
            return self._run_streaming(user_message, max_iterations)
        return self._run_non_streaming(user_message, max_iterations)
    
    def _run_non_streaming(self, user_message: str, max_iterations: Optional[int] = None) -> str:
        """Non-streaming version of run (original implementation)."""
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
    
    def _run_streaming(self, user_message: str, max_iterations: Optional[int] = None):
        """Streaming version of run - yields response chunks as they arrive."""
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
            yield f"\n🤖 Processing: {user_message}\n\n"
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            if self.verbose:
                yield f"[Iteration {iteration}]\n"
            
            try:
                # Call LiteLLM with streaming enabled
                response = self.client.chat.completions.create(
                    model=AgentConfig.MODEL_NAME,
                    max_tokens=AgentConfig.MAX_TOKENS,
                    temperature=AgentConfig.TEMPERATURE,
                    messages=messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    tool_choice="auto",
                    stream=True
                )
                
                # Collect the streamed response
                accumulated_content = ""
                tool_calls_data = []
                current_tool_call = None
                
                for chunk in response:
                    if not chunk.choices:
                        continue
                    
                    delta = chunk.choices[0].delta
                    
                    # Handle content streaming
                    if delta.content:
                        accumulated_content += delta.content
                        yield delta.content
                    
                    # Handle tool calls
                    if delta.tool_calls:
                        for tc_delta in delta.tool_calls:
                            if tc_delta.index is not None:
                                # Ensure we have enough slots
                                while len(tool_calls_data) <= tc_delta.index:
                                    tool_calls_data.append({
                                        "id": None,
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    })
                                
                                current_tool_call = tool_calls_data[tc_delta.index]
                                
                                if tc_delta.id:
                                    current_tool_call["id"] = tc_delta.id
                                if tc_delta.function:
                                    if tc_delta.function.name:
                                        current_tool_call["function"]["name"] = tc_delta.function.name
                                    if tc_delta.function.arguments:
                                        current_tool_call["function"]["arguments"] += tc_delta.function.arguments
                
                # Check if we got tool calls
                if tool_calls_data and any(tc["id"] for tc in tool_calls_data):
                    import time
                    
                    # Start collapsible tool section
                    yield "\n\n<details open style='background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 4px solid #3b82f6; border-radius: 12px; padding: 16px; margin: 12px 0; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);'>\n"
                    yield f"<summary style='cursor: pointer; font-weight: 600; color: #1e40af; font-size: 15px; display: flex; align-items: center; gap: 8px;'>\n"
                    yield f"<span style='font-size: 18px;'>🔧</span> **Tool Execution** ({len(tool_calls_data)} tool{'s' if len(tool_calls_data) > 1 else ''})\n"
                    yield "</summary>\n\n"
                    
                    # Add assistant's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": accumulated_content,
                        "tool_calls": tool_calls_data
                    })
                    
                    # Execute all requested tools
                    for idx, tool_call in enumerate(tool_calls_data, 1):
                        tool_name = tool_call["function"]["name"]
                        tool_args_str = tool_call["function"]["arguments"]
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                        
                        # Tool metadata
                        tool_info = {
                            "get_current_weather": {"emoji": "🌤️", "name": "Weather Forecast", "color": "#0ea5e9"},
                            "search_books": {"emoji": "📚", "name": "Book Search", "color": "#8b5cf6"},
                            "get_random_joke": {"emoji": "😄", "name": "Joke Generator", "color": "#f59e0b"},
                            "get_dog_image": {"emoji": "🐕", "name": "Dog Picture", "color": "#ec4899"},
                            "get_trivia_question": {"emoji": "🎯", "name": "Trivia Question", "color": "#10b981"}
                        }
                        info = tool_info.get(tool_name, {"emoji": "🔧", "name": tool_name.replace('_', ' ').title(), "color": "#6366f1"})
                        
                        # Start individual tool card
                        yield f"<div style='background: white; border-radius: 10px; padding: 14px; margin: 10px 0; border-left: 3px solid {info['color']}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>\n"
                        
                        # Tool header
                        yield f"<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>\n"
                        yield f"<span style='font-size: 24px;'>{info['emoji']}</span>\n"
                        yield f"<span style='font-weight: 600; color: {info['color']}; font-size: 14px;'>#{idx} {info['name']}</span>\n"
                        yield "</div>\n"
                        
                        # Parameters section
                        if tool_args:
                            yield "<div style='background: #f8fafc; border-radius: 6px; padding: 10px; margin: 8px 0; font-family: monospace; font-size: 13px;'>\n"
                            yield "<span style='color: #64748b; font-weight: 600;'>Parameters:</span>\n"
                            for k, v in tool_args.items():
                                yield f"<div style='margin-left: 12px; color: #334155;'>• <code style='background: #e2e8f0; padding: 2px 6px; border-radius: 4px;'>{k}</code>: {v}</div>\n"
                            yield "</div>\n"
                        else:
                            yield "<div style='color: #94a3b8; font-size: 13px; font-style: italic;'>No parameters</div>\n"
                        
                        # Execute tool with timing
                        yield "<div style='display: flex; align-items: center; gap: 8px; margin-top: 10px;'>\n"
                        yield "<span style='color: #64748b; font-size: 13px;'>Status:</span>\n"
                        
                        start_time = time.time()
                        try:
                            result = self.tool_registry.execute_tool(tool_name, tool_args)
                            elapsed = (time.time() - start_time) * 1000  # Convert to ms
                            
                            yield f"<span style='background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 12px;'>✓ SUCCESS</span>\n"
                            yield f"<span style='color: #64748b; font-size: 12px;'>• {elapsed:.0f}ms</span>\n"
                            
                            # Show result preview
                            result_str = json.dumps(result, indent=2)
                            if len(result_str) > 200:
                                result_preview = result_str[:200] + "..."
                            else:
                                result_preview = result_str
                            
                            yield "</div>\n"
                            yield f"<details style='margin-top: 8px;'>\n"
                            yield f"<summary style='cursor: pointer; color: #64748b; font-size: 12px;'>📄 View response data</summary>\n"
                            yield f"<pre style='background: #f1f5f9; padding: 10px; border-radius: 6px; overflow-x: auto; font-size: 12px; margin-top: 6px;'>{result_preview}</pre>\n"
                            yield "</details>\n"
                            
                        except Exception as e:
                            elapsed = (time.time() - start_time) * 1000
                            result = {"error": str(e)}
                            
                            yield f"<span style='background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 12px;'>✗ FAILED</span>\n"
                            yield f"<span style='color: #64748b; font-size: 12px;'>• {elapsed:.0f}ms</span>\n"
                            yield "</div>\n"
                            yield f"<div style='background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 10px; margin-top: 8px; color: #991b1b; font-size: 13px;'>\n"
                            yield f"<strong>Error:</strong> {str(e)}\n"
                            yield "</div>\n"
                        
                        yield "</div>\n"  # Close tool card
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": json.dumps(result)
                        })
                    
                    yield "\n</details>\n\n"  # Close collapsible section
                    if self.verbose:
                        yield "\n"
                
                elif accumulated_content:
                    # Model provided final answer
                    if self.verbose:
                        yield "\n✓ Final answer provided\n"
                    return
                    
            except Exception as e:
                if self.verbose:
                    yield f"\n❌ Error in iteration {iteration}: {e}\n"
                raise
        
        # Max iterations reached
        if self.verbose:
            yield f"\n⚠ Max iterations ({max_iterations}) reached\n"
    
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
