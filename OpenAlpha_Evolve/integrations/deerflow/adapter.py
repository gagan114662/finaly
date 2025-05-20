import requests
import logging
from .config import DeerFlowConfig

logger = logging.getLogger(__name__)

class DeerFlowAdapter:
    def __init__(self, config: DeerFlowConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}" if config.api_key else None
        })
    
    def get_tools(self):
        try:
            response = self.session.get(
                f"{self.config.api_url}/tools",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch DeerFlow tools: {str(e)}")
            return []