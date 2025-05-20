from pydantic import BaseModel, Field
from typing import Optional

class DeerFlowConfig(BaseModel):
    """Configuration for DeerFlow integration."""
    
    # TTS API Configuration
    tts_endpoint: str = "http://localhost:8000/api/tts"
    tts_default_speed: float = 1.0
    tts_default_volume: float = 1.0
    tts_default_pitch: float = 1.0

    # LangGraph Configuration
    langgraph_studio_url: str = "https://smith.langchain.com/studio/"
    langgraph_api_url: str = "http://127.0.0.1:2024"
    
    # LangSmith Tracing Configuration
    langsmith_tracing: bool = True
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = "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"
    langsmith_project: str = "deerflow-integration"

    # Workflow Settings
    max_plan_iterations: int = 3
    max_step_num: int = 5
    enable_human_review: bool = True

    # Docker Configuration
    docker_image: str = "deer-flow-api"
    docker_port: int = 8000

    class Config:
        extra = "forbid"
        env_file = ".env"
        env_file_encoding = "utf-8"