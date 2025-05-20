from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DeerFlowConfig:
    enabled: bool = False
    api_url: str = "http://localhost:8000"
    timeout: int = 30
    tools: List[str] = None
    api_key: Optional[str] = None