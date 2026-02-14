"""Configuration for the LiteLLM Agent implementation."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class AgentConfig:
    """Configuration for the L2 Wizard Agent."""
    
    # API Keys
    DEEPINFRA_API_KEY: Optional[str] = os.environ.get("DEEPINFRA_API_KEY")
    
    # LiteLLM Proxy Configuration
    LITELLM_BASE_URL: str = "https://litellm-api.predev.praveg.ai/v1"
    
    # Model selection (using DeepInfra via LiteLLM)
    MODEL_NAME: str = "deepinfra/Qwen/Qwen2.5-72B-Instruct"
    
    # Agent behavior
    MAX_ITERATIONS: int = 10
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # Tool timeouts
    TOOL_TIMEOUT: int = 20
    
    # Logging
    VERBOSE: bool = True
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.DEEPINFRA_API_KEY:
            raise ValueError(
                "DEEPINFRA_API_KEY not found. "
                "Add it to your .env file."
            )
