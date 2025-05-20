                      
import os
from dotenv import load_dotenv
from OpenAlpha_Evolve.integrations.deerflow.config import DeerFlowConfig

load_dotenv()

# Deer-Flow Integration Configuration
DEERFLOW = DeerFlowConfig(
    enabled=os.getenv("DEERFLOW_ENABLED", "false").lower() == "true",
    api_url=os.getenv("DEERFLOW_API_URL", "http://localhost:8000"),
    api_key=os.getenv("DEERFLOW_API_KEY"),
    tools=["research_agent", "data_crawler", "report_generator"]
)

# API Configuration
FLASH_API_KEY = os.getenv("FLASH_API_KEY")
PRO_API_KEY = os.getenv("PRO_API_KEY")
EVALUATION_API_KEY = os.getenv("EVALUATION_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")

if not EVALUATION_API_KEY:
    print("Warning: EVALUATION_API_KEY not found in .env or environment")

# Model names
FLASH_MODEL_NAME = "gemini-2.0-flash"
PRO_MODEL_NAME = "gemini-2.0-flash"
EVALUATION_MODEL = "gpt-4o"

                                    
POPULATION_SIZE = 5                                            
GENERATIONS = 2                                                   
ELITISM_COUNT = 1                                                                      
MUTATION_RATE = 0.7                                          
CROSSOVER_RATE = 0.2                                                                          

                     
EVALUATION_TIMEOUT_SECONDS = 800                                                   

                                                            
DATABASE_TYPE = "in_memory"                                          
DATABASE_PATH = "program_database.json"                         

                    
LOG_LEVEL = "INFO"                                        
LOG_FILE = "alpha_evolve.log"

                      
API_MAX_RETRIES = 5
API_RETRY_DELAY_SECONDS = 10                                     

                                                 
RL_TRAINING_INTERVAL_GENERATIONS = 50                                         
RL_MODEL_PATH = "rl_finetuner_model.pth"

                             
MONITORING_DASHBOARD_URL = "http://localhost:8080"          

                                                   
def get_setting(key, default=None):
    """
    Retrieves a setting value.
    For LLM models, it specifically checks if the primary choice is available,
    otherwise falls back to a secondary/default if defined.
    """
                                                                  
                                                                     
    return globals().get(key, default)

                                                                                                                     
def get_llm_model(model_type="pro"):
    if model_type == "pro":
        return PRO_MODEL_NAME if PRO_API_KEY else None
    elif model_type == "flash":
        return FLASH_MODEL_NAME if FLASH_API_KEY else None
    return EVALUATION_MODEL if EVALUATION_API_KEY else None

                                 
