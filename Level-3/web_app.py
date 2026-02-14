"""Gradio Web Interface for L2 Wizard Agent."""

import gradio as gr
from agent import LiteLLMAgent
from config import AgentConfig
import traceback


class WebInterface:
    """Web interface for the L2 Wizard agent using Gradio."""
    
    def __init__(self):
        """Initialize the web interface."""
        try:
            AgentConfig.validate()
            self.agent = LiteLLMAgent(verbose=False)  # Disable verbose for cleaner UI
            self.is_ready = True
            self.error_message = None
        except Exception as e:
            self.is_ready = False
            self.error_message = str(e)
    
    def chat(self, message, history, stream_output: bool = True):
        """
        Process a chat message and return the response.
        
        Args:
            message: User's input message
            history: Chat history (list of message dicts with 'role' and 'content')
            stream_output: Whether to stream the response
            
        Yields:
            Updated chat history with new messages
        """
        if not self.is_ready:
            error_msg = f"❌ Configuration Error: {self.error_message}\n\nPlease set the DEEPINFRA_API_KEY environment variable or add it to your .env file."
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            yield history
            return
        
        if not message.strip():
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": "Please enter a message."})
            yield history
            return
        
        # Add user message to history and show it immediately
        history.append({"role": "user", "content": message})
        yield history  # Show user message right away
        
        try:
            if stream_output:
                # Streaming mode - show thinking indicator, then stream response
                history.append({"role": "assistant", "content": "🤔 Thinking..."})
                yield history
                
                response_text = ""
                for chunk in self.agent.run(message, stream=True):
                    response_text += chunk
                    history[-1]["content"] = response_text
                    yield history
            else:
                # Non-streaming mode - show thinking indicator, then complete response
                history.append({"role": "assistant", "content": "🤔 Processing your request..."})
                yield history
                
                response = self.agent.run(message, stream=False)
                history[-1]["content"] = response
                yield history
                
        except Exception as e:
            # Format user-friendly error messages
            error_type = type(e).__name__
            
            if "timeout" in str(e).lower() or "APITimeoutError" in error_type:
                error_msg = f"""❌ **Connection Timeout**

The request to the LiteLLM proxy timed out. This could mean:
- The proxy server is slow or unreachable
- Network connectivity issues
- The model is taking too long to respond

**Troubleshooting:**
1. Check if the proxy is accessible: `{AgentConfig.LITELLM_BASE_URL}`
2. Verify your internet connection
3. Try again with a shorter query
4. Try disabling streaming mode

**Technical Details:**
```
{str(e)}
```"""
            elif "ConnectError" in error_type or "connection" in str(e).lower():
                error_msg = f"""❌ **Connection Failed**

Could not connect to the LiteLLM proxy at:
`{AgentConfig.LITELLM_BASE_URL}`

**Troubleshooting:**
1. Verify the proxy URL is correct
2. Check if the proxy is running
3. Test connectivity: `curl {AgentConfig.LITELLM_BASE_URL}/health`
4. Check firewall/proxy settings

**Technical Details:**
```
{str(e)}
```"""
            else:
                error_msg = f"❌ **Error:** {str(e)}\n\n```\n{traceback.format_exc()}\n```"
            
            history.append({"role": "assistant", "content": error_msg})
            yield history
    
    def create_interface(self):
        """Create and configure the Gradio interface."""
        
        # Custom CSS for professional, modern styling
        self.custom_css = """
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }
        
        /* Main Container */
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto !important;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
            min-height: 100vh;
            padding: 20px;
        }
        
        /* Header Styling */
        .header-banner {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            padding: 50px 30px;
            border-radius: 24px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(30, 64, 175, 0.25);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .header-title {
            font-size: 42px;
            font-weight: 700;
            color: white;
            margin: 0 0 10px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header-subtitle {
            font-size: 18px;
            color: rgba(255,255,255,0.9);
            font-weight: 400;
        }
        
        /* Info Cards */
        .info-card {
            background: white;
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(30, 64, 175, 0.08);
            border-left: 4px solid #3b82f6;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(30, 64, 175, 0.12);
        }
        
        .info-card h3 {
            color: #1e40af;
            font-size: 18px;
            font-weight: 600;
            margin-top: 0;
        }
        
        /* Tool Badges */
        .tools-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .tool-badge {
            display: inline-flex;
            align-items: center;
            padding: 12px 20px;
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .tool-badge:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        }
        
        /* Chat Container - Enhanced Professional */
        .chatbot-container {
            background: white !important;
            border-radius: 24px !important;
            box-shadow: 0 10px 40px rgba(30, 64, 175, 0.15) !important;
            border: 2px solid #e0e7ff !important;
            padding: 24px !important;
            min-height: 550px !important;
        }
        
        /* Gradio Chat Bubbles - User Messages */
        .chatbot .user {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
            color: white !important;
            border-radius: 20px 20px 4px 20px !important;
            padding: 16px 22px !important;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35) !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
            font-weight: 500 !important;
            margin: 8px 0 !important;
            max-width: 75% !important;
            word-wrap: break-word !important;
        }
        
        /* Gradio Chat Bubbles - Bot Messages */
        .chatbot .bot {
            background: white !important;
            color: #1e293b !important;
            border: 2px solid #e0e7ff !important;
            border-radius: 20px 20px 20px 4px !important;
            padding: 16px 22px !important;
            box-shadow: 0 3px 12px rgba(30, 64, 175, 0.12) !important;
            font-size: 15px !important;
            line-height: 1.7 !important;
            margin: 8px 0 !important;
            max-width: 85% !important;
            word-wrap: break-word !important;
        }
        
        /* Chat message container background */
        .chatbot {
            background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%) !important;
            border-radius: 20px !important;
            padding: 16px !important;
        }
        
        /* Fallback message styling */
        .message {
            padding: 16px 22px;
            border-radius: 20px;
            margin: 10px 0;
            max-width: 80%;
            line-height: 1.6;
            font-size: 15px;
            word-wrap: break-word;
        }
        
        .message.user {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            margin-left: auto;
            border-radius: 20px 20px 4px 20px;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
            font-weight: 500;
        }
        
        .message.bot {
            background: white;
            color: #1e293b;
            border: 2px solid #e0e7ff;
            border-radius: 20px 20px 20px 4px;
            box-shadow: 0 3px 12px rgba(30, 64, 175, 0.12);
        }
        
        /* Tool Call Sections - Enhanced Styling */
        .bot details {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
            border-left: 4px solid #3b82f6 !important;
            border-radius: 12px !important;
            padding: 16px !important;
            margin: 12px 0 !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        }
        
        .bot details summary {
            cursor: pointer !important;
            font-weight: 600 !important;
            color: #1e40af !important;
            font-size: 15px !important;
            list-style: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 4px !important;
            border-radius: 8px !important;
            transition: background 0.2s !important;
        }
        
        .bot details summary:hover {
            background: rgba(59, 130, 246, 0.1) !important;
        }
        
        .bot details summary::-webkit-details-marker {
            display: none !important;
        }
        
        .bot details[open] summary::before {
            content: '▼' !important;
            font-size: 12px !important;
            color: #3b82f6 !important;
            margin-right: 4px !important;
        }
        
        .bot details:not([open]) summary::before {
            content: '▶' !important;
            font-size: 12px !important;
            color: #3b82f6 !important;
            margin-right: 4px !important;
        }
        
        /* Individual Tool Cards */
        .bot details > div {
            background: white !important;
            border-radius: 10px !important;
            padding: 14px !important;
            margin: 10px 0 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
        }
        
        .bot details > div:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
        }
        
        /* Code blocks in tool responses */
        .bot pre {
            background: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 12px !important;
            overflow-x: auto !important;
            font-size: 12px !important;
            line-height: 1.5 !important;
            color: #334155 !important;
        }
        
        .bot code {
            background: #e2e8f0 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-size: 13px !important;
            color: #1e293b !important;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace !important;
        }
        
        /* Success/Error badges */
        .bot details span[style*='#dcfce7'] {
            animation: successPulse 0.5s ease-out !important;
        }
        
        .bot details span[style*='#fee2e2'] {
            animation: errorShake 0.5s ease-out !important;
        }
        
        @keyframes successPulse {
            0% { transform: scale(0.9); opacity: 0; }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        @keyframes errorShake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-4px); }
            75% { transform: translateX(4px); }
        }
        
        /* Input Area - Enhanced Professional Design */
        .input-container {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 30px rgba(30, 64, 175, 0.12);
            margin-top: 25px;
            border: 2px solid #e0e7ff;
            transition: all 0.3s;
        }
        
        .input-container:hover {
            border-color: #c7d2fe;
            box-shadow: 0 12px 40px rgba(30, 64, 175, 0.15);
        }
        
        /* Query Input Styling */
        textarea {
            border: 2px solid #e0e7ff !important;
            border-radius: 16px !important;
            padding: 18px 20px !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: #f8fafc !important;
            resize: none !important;
        }
        
        textarea:hover {
            border-color: #c7d2fe !important;
            background: white !important;
        }
        
        textarea:focus {
            border-color: #3b82f6 !important;
            outline: none !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
            background: white !important;
            transform: translateY(-1px);
        }
        
        /* Input Placeholder */
        textarea::placeholder {
            color: #94a3b8 !important;
            font-weight: 400 !important;
        }
        
        /* Buttons - Professional Design */
        .primary-button {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 16px 32px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .primary-button::before {
            content: '' !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            width: 0 !important;
            height: 0 !important;
            border-radius: 50% !important;
            background: rgba(255, 255, 255, 0.2) !important;
            transform: translate(-50%, -50%) !important;
            transition: width 0.6s, height 0.6s !important;
        }
        
        .primary-button:hover::before {
            width: 300px !important;
            height: 300px !important;
        }
        
        .primary-button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.4) !important;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        }
        
        .primary-button:active {
            transform: translateY(-1px) scale(0.98) !important;
        }
        
        .secondary-button {
            background: white !important;
            color: #2563eb !important;
            border: 2px solid #2563eb !important;
            border-radius: 16px !important;
            padding: 14px 28px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1) !important;
        }
        
        .secondary-button:hover {
            background: #2563eb !important;
            color: white !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* Checkbox/Toggle */
        .checkbox-container {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            margin: 15px 0;
        }
        
        /* Example Cards */
        .example-card {
            background: white;
            border: 2px solid #e0e7ff;
            border-radius: 14px;
            padding: 16px 22px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin: 8px;
            box-shadow: 0 2px 8px rgba(30, 64, 175, 0.05);
        }
        
        .example-card:hover {
            border-color: #3b82f6;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            transform: translateX(8px) translateY(-2px);
            box-shadow: 0 8px 20px rgba(30, 64, 175, 0.15);
        }
        
        /* Status Indicators */
        .status-ready {
            display: inline-block;
            padding: 6px 12px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }
        
        .status-error {
            display: inline-block;
            padding: 6px 12px;
            background: #ef4444;
            color: white;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }
        
        /* Accordion */
        .accordion {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            color: #6b7280;
            font-size: 14px;
            margin-top: 40px;
        }
        
        .footer-link {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }
        
        .footer-link:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Thinking indicator animation */
        @keyframes thinking {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { 
                opacity: 0; 
                transform: translateX(-20px); 
            }
            to { 
                opacity: 1; 
                transform: translateX(0); 
            }
        }
        
        /* Apply animations */
        .bot:has-text("🤔") {
            animation: thinking 1.5s ease-in-out infinite;
        }
        
        .tool-indicator {
            animation: slideInLeft 0.3s ease-out;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        }
        """
        
        # Create the interface
        with gr.Blocks(title="L2 Wizard - AI Agent Platform") as interface:
            # Professional Header
            gr.HTML("""
                <div class="header-banner fade-in">
                    <div class="header-title">🧙‍♂️ L2 Wizard</div>
                    <div class="header-subtitle">Intelligent AI Agent with Multi-Tool Capabilities</div>
                </div>
            """)
            
            # Configuration info with modern card design
            with gr.Accordion("⚙️ System Configuration & Available Tools", open=False):
                if self.is_ready:
                    gr.HTML(f"""
                    <div class="info-card">
                        <h3>🚀 System Status</h3>
                        <div style="display: flex; align-items: center; gap: 15px; margin-top: 10px;">
                            <span class="status-ready">● READY</span>
                            <div style="flex: 1;">
                                <div style="margin-bottom: 8px;"><strong>Model:</strong> <code>{AgentConfig.MODEL_NAME}</code></div>
                                <div><strong>Proxy:</strong> <code>{AgentConfig.LITELLM_BASE_URL}</code></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <h3>🛠️ Available Tools</h3>
                        <p style="color: #6b7280; margin-bottom: 15px;">
                            This agent has access to the following specialized tools:
                        </p>
                        <div class="tools-container">
                            <div class="tool-badge">🌤️ Weather Forecast</div>
                            <div class="tool-badge">📚 Book Recommendations</div>
                            <div class="tool-badge">😄 Joke Generator</div>
                            <div class="tool-badge">🐕 Dog Pictures</div>
                            <div class="tool-badge">🎯 Trivia Questions</div>
                        </div>
                    </div>
                    """)
                else:
                    gr.HTML(f"""
                    <div class="info-card" style="border-left-color: #ef4444;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span class="status-error">● ERROR</span>
                            <div>
                                <h3 style="color: #ef4444; margin: 0;">Configuration Error</h3>
                                <p style="margin: 10px 0 0 0; color: #6b7280;">{self.error_message}</p>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding: 15px; background: #fef2f2; border-radius: 8px; border-left: 3px solid #ef4444;">
                            <strong>Action Required:</strong><br>
                            Please set the <code>DEEPINFRA_API_KEY</code> in your <code>.env</code> file or environment variables.
                        </div>
                    </div>
                    """)
            
            # Example queries with modern card design
            with gr.Accordion("💡 Example Queries & Use Cases", open=False):
                gr.HTML("""
                <div class="info-card">
                    <h3>Try These Example Queries:</h3>
                    <p style="color: #6b7280; margin-bottom: 15px;">
                        Click any example below or type your own query. The agent will automatically select and use the appropriate tools.
                    </p>
                    <div style="display: grid; gap: 10px;">
                        <div class="example-card">
                            <strong>🌍 Weather Query:</strong> What's the weather in New York at (40.7128, -74.0060)?
                        </div>
                        <div class="example-card">
                            <strong>📖 Reading Request:</strong> Recommend 3 mystery books
                        </div>
                        <div class="example-card">
                            <strong>🎭 Entertainment:</strong> Tell me a joke and show me a dog picture
                        </div>
                        <div class="example-card">
                            <strong>🎯 Knowledge Test:</strong> Give me a trivia question
                        </div>
                        <div class="example-card">
                            <strong>🗓️ Complex Planning:</strong> Plan a Saturday in Paris at (48.8566, 2.3522). Get weather, recommend 2 mystery books, and give me a trivia question.
                        </div>
                    </div>
                </div>
                """)
            
            # Main chat interface with modern design
            gr.HTML("""
                <div style="margin: 30px 0 15px 0;">
                    <h2 style="font-size: 24px; font-weight: 600; color: #1f2937; margin: 0;">
                        💬 Chat Interface
                    </h2>
                    <p style="color: #6b7280; margin: 8px 0 0 0;">
                        Start a conversation with the AI agent
                    </p>
                </div>
            """)
            
            chatbot = gr.Chatbot(
                label="",
                height=550,
                container=True,
                elem_classes="chatbot-container"
            )
            
            # Input section with professional design
            gr.HTML("""
                <div style="margin-top: 30px; padding: 20px; background: white; border-radius: 20px; border: 2px solid #e0e7ff; box-shadow: 0 4px 20px rgba(30, 64, 175, 0.08);">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="width: 4px; height: 24px; background: linear-gradient(135deg, #2563eb, #3b82f6); border-radius: 4px;"></div>
                        <h3 style="margin: 0; font-size: 18px; font-weight: 600; color: #1e40af;">💬 Your Query</h3>
                    </div>
                    <p style="margin: 0 0 15px 0; color: #64748b; font-size: 14px; padding-left: 16px;">
                        Type your question or request below. I'll automatically use the right tools to help you!
                    </p>
                </div>
            """)
            
            gr.HTML("""<div style="margin-top: 15px;"></div>""")
            
            with gr.Row():
                msg = gr.Textbox(
                    label="",
                    placeholder="✨ Ask me anything! Examples: 'What's the weather in Paris?', 'Recommend a mystery book', 'Tell me a joke'...",
                    lines=3,
                    scale=4,
                    container=False,
                    elem_classes="query-input"
                )
            
            with gr.Row():
                with gr.Column(scale=3):
                    stream_checkbox = gr.Checkbox(
                        label="⚡ Enable Real-time Streaming",
                        value=True,
                        info="See responses as they're generated",
                        container=False
                    )
                with gr.Column(scale=1):
                    send_btn = gr.Button(
                        "Send 🚀",
                        variant="primary",
                        size="lg",
                        elem_classes="primary-button"
                    )
                with gr.Column(scale=1):
                    clear_btn = gr.Button(
                        "Clear 🗑️",
                        size="lg",
                        elem_classes="secondary-button"
                    )
            
            # Quick examples
            gr.HTML("""<div style="margin-top: 25px;"></div>""")
            gr.Examples(
                examples=[
                    ["What's the weather in Tokyo at (35.6762, 139.6503)?"],
                    ["Recommend 2 science fiction books"],
                    ["Tell me a programming joke"],
                    ["Show me a cute dog picture"],
                    ["Give me a science trivia question"],
                    ["Plan a cozy Saturday: weather for NYC (40.7128, -74.0060), 2 mystery books, a joke, and a dog pic"]
                ],
                inputs=msg,
                label="⚡ Quick Start Examples",
                examples_per_page=6
            )
            
            # Event handlers
            def submit_message(message, history, stream):
                """Handle message submission."""
                if message.strip():
                    yield from self.chat(message, history, stream)
            
            msg.submit(
                fn=submit_message,
                inputs=[msg, chatbot, stream_checkbox],
                outputs=chatbot,
            ).then(
                lambda: gr.Textbox(value=""),
                outputs=msg
            )
            
            send_btn.click(
                fn=submit_message,
                inputs=[msg, chatbot, stream_checkbox],
                outputs=chatbot,
            ).then(
                lambda: gr.Textbox(value=""),
                outputs=msg
            )
            
            clear_btn.click(
                lambda: [],
                outputs=chatbot
            )
            
            # Professional Footer
            gr.HTML("""
                <div class="footer">
                    <div style="max-width: 800px; margin: 0 auto;">
                        <div style="font-size: 16px; font-weight: 600; color: #2563eb; margin-bottom: 15px;">
                            🧙‍♂️ L2 Wizard - Level 3 Implementation
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong>Powered by:</strong> 
                            <a href="https://litellm.ai" class="footer-link" target="_blank">LiteLLM</a> • 
                            <a href="https://deepinfra.com" class="footer-link" target="_blank">DeepInfra</a> • 
                            <a href="https://gradio.app" class="footer-link" target="_blank">Gradio</a>
                        </div>
                        <div style="font-size: 13px; color: #9ca3af;">
                            APIs: Open-Meteo • Google Books • JokeAPI • Dog CEO • Open Trivia DB
                        </div>
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
                            © 2026 L2 Wizard. Built with modern AI technologies.
                        </div>
                    </div>
                </div>
            """)
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        
        # Default launch settings
        launch_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "show_error": True,
            "css": self.custom_css,  # CSS moved to launch() in Gradio 6.0
            **kwargs
        }
        
        print("=" * 70)
        print("🧙‍♂️  L2 WIZARD - AI AGENT PLATFORM")
        print("=" * 70)
        print(f"\n📡 Model:  {AgentConfig.MODEL_NAME}")
        print(f"🔌 Proxy:  {AgentConfig.LITELLM_BASE_URL}")
        print(f"\n🚀 Launching web interface...")
        print(f"📍 Local:  http://localhost:{launch_kwargs['server_port']}")
        if launch_kwargs['share']:
            print("🌐 Creating shareable public link...")
        print("\n" + "=" * 70)
        print("✨ Interface ready! Open the URL above in your browser.")
        print("=" * 70 + "\n")
        
        interface.launch(**launch_kwargs)


def main():
    """Main entry point for the web interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧙‍♂️ L2 Wizard - AI Agent Platform with Multi-Tool Capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_app.py                    # Launch on default port 7860
  python web_app.py --port 8080        # Launch on custom port
  python web_app.py --share            # Create public shareable link
  python web_app.py --host 0.0.0.0     # Allow external connections
        """
    )
    parser.add_argument("--port", type=int, default=7860, help="Port to run on (default: 7860)")
    parser.add_argument("--share", action="store_true", help="Create a shareable public link")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    try:
        web_interface = WebInterface()
        web_interface.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error launching web interface: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
