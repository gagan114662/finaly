                                           
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class Program:
    id: str
    code: str
    fitness_scores: Dict[str, float] = field(default_factory=lambda: {
        "correctness": 0.0,
        "runtime_ms": float('inf'),
        "sharpe_ratio": 0,
        "max_drawdown": 0,
        "total_return": 0,
        "win_rate": 0,
        "profit_factor": 1
    })
    generation: int = 0
    parent_id: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    status: str = "unevaluated"
    version: str = "1.0.0"
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())

@dataclass
class StrategyProgram(Program):
    parameters: Dict[str, Any] = field(default_factory=dict)
    market_regime: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    version_history: List[Dict[str, Any]] = field(default_factory=list)
    backtest_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskDefinition:
    id: str
    description: str
    function_name_to_evolve: Optional[str] = None
    input_output_examples: Optional[List[Dict[str, Any]]] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    initial_code_prompt: Optional[str] = "Provide an initial Python solution for the following problem:"
    allowed_imports: Optional[List[str]] = None
    task_type: str = "generic"  # "generic" or "strategy"
    backtest_symbol: Optional[str] = None
    backtest_start_date: Optional[str] = None
    backtest_end_date: Optional[str] = None
    initial_capital: float = 100000.0

class BaseAgent(ABC):
    """Base class for all agents."""
    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Main execution method for an agent."""
        pass

class TaskManagerInterface(BaseAgent):
    @abstractmethod
    async def manage_evolutionary_cycle(self):
        pass

class PromptDesignerInterface(BaseAgent):
    @abstractmethod
    def design_initial_prompt(self, task: TaskDefinition) -> str:
        pass

    @abstractmethod
    def design_mutation_prompt(self, task: TaskDefinition, parent_program: Program, evaluation_feedback: Optional[Dict] = None) -> str:
        pass

    @abstractmethod
    def design_bug_fix_prompt(self, task: TaskDefinition, program: Program, error_info: Dict) -> str:
        pass

class CodeGeneratorInterface(BaseAgent):
    @abstractmethod
    async def generate_code(self, prompt: str, model_name: Optional[str] = None, temperature: Optional[float] = 0.7, output_format: str = "code") -> str:
        pass

class EvaluatorAgentInterface(BaseAgent):
    @abstractmethod
    async def evaluate_program(self, program: Program, task: TaskDefinition) -> Program:
        pass

class DatabaseAgentInterface(BaseAgent):
    @abstractmethod
    async def save_program(self, program: Union[Program, StrategyProgram]):
        pass

    @abstractmethod
    async def get_program(self, program_id: str) -> Optional[Union[Program, StrategyProgram]]:
        pass

    @abstractmethod
    async def get_best_programs(self, task_id: str, limit: int = 10, objective: Optional[str] = None) -> List[Union[Program, StrategyProgram]]:
        pass
    
    @abstractmethod
    async def get_programs_for_next_generation(self, task_id: str, generation_size: int) -> List[Union[Program, StrategyProgram]]:
        pass

    @abstractmethod
    async def get_program_versions(self, program_id: str) -> List[Dict[str, Any]]:
        """Get version history for a program"""
        pass

    @abstractmethod
    async def get_programs_by_regime(self, regime: str) -> List[StrategyProgram]:
        """Get all strategies that performed well in given market regime"""
        pass

    @abstractmethod
    async def get_programs_by_parameter(self, param_name: str, param_value: Any) -> List[StrategyProgram]:
        """Get strategies with specific parameter values"""
        pass

class SelectionControllerInterface(BaseAgent):
    @abstractmethod
    def select_parents(self, evaluated_programs: List[Program], num_parents: int) -> List[Program]:
        pass

    @abstractmethod
    def select_survivors(self, current_population: List[Program], offspring_population: List[Program], population_size: int) -> List[Program]:
        pass

class RLFineTunerInterface(BaseAgent):
    @abstractmethod
    async def update_policy(self, experience_data: List[Dict]):
        pass

class MonitoringAgentInterface(BaseAgent):
    @abstractmethod
    async def log_metrics(self, metrics: Dict):
        pass

    @abstractmethod
    async def report_status(self):
        pass

                                                                      