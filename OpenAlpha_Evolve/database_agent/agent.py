                 
import logging
from typing import List, Dict, Any, Optional, Literal
import uuid

from OpenAlpha_Evolve.core.interfaces import (
    DatabaseAgentInterface,
    Program,
    BaseAgent,
)
                                                               

logger = logging.getLogger(__name__)

from typing import Dict, List, Optional, Any, Union, Tuple
import time
from OpenAlpha_Evolve.core.interfaces import Program, StrategyProgram

class InMemoryDatabaseAgent(DatabaseAgentInterface, BaseAgent):
    """An in-memory database for storing and retrieving programs."""
    def __init__(self):
        super().__init__()
        self._programs: Dict[str, Union[Program, StrategyProgram]] = {}
        self._version_history: Dict[str, List[Dict[str, Any]]] = {}
        self._regime_index: Dict[str, List[str]] = {}
        self._parameter_index: Dict[Tuple[str, Any], List[str]] = {}
        self._ast_pattern_index: Dict[str, List[str]] = {}
        self._error_type_index: Dict[str, List[str]] = {}
        self._performance_index: Dict[Tuple[str, float], List[str]] = {}
        self._api_usage_index: Dict[str, List[str]] = {}
        logger.info("InMemoryDatabaseAgent initialized.")

    async def save_program(self, program: Union[Program, StrategyProgram]) -> None:
        logger.info(f"Saving program: {program.id} (Generation: {program.generation}) to in-memory database.")
        
        # Handle versioning
        if program.id in self._programs:
            logger.warning(f"Program with ID {program.id} already exists. Creating new version.")
            old_version = self._programs[program.id]
            version_entry = {
                'version': old_version.version,
                'code': old_version.code,
                'fitness_scores': old_version.fitness_scores,
                'timestamp': old_version.updated_at
            }
            self._version_history.setdefault(program.id, []).append(version_entry)
        
        # Update program
        program.updated_at = time.time()
        self._programs[program.id] = program
        
        # Index strategy-specific data
        if isinstance(program, StrategyProgram):
            if program.market_regime:
                self._regime_index.setdefault(program.market_regime, []).append(program.id)
            for param_name, param_value in program.parameters.items():
                self._parameter_index.setdefault((param_name, param_value), []).append(program.id)
        
        # Index additional metrics if available
        if hasattr(program, 'ast_patterns'):
            for pattern in program.ast_patterns:
                self._ast_pattern_index.setdefault(pattern, []).append(program.id)
        
        if hasattr(program, 'error_types'):
            for error_type in program.error_types:
                self._error_type_index.setdefault(error_type, []).append(program.id)
        
        if hasattr(program, 'performance_metrics'):
            for metric_name, metric_value in program.performance_metrics.items():
                self._performance_index.setdefault((metric_name, metric_value), []).append(program.id)
        
        if hasattr(program, 'api_usage'):
            for api_call in program.api_usage:
                self._api_usage_index.setdefault(api_call, []).append(program.id)
        
        logger.debug(f"Program {program.id} data: {program}")

    async def get_program(self, program_id: str) -> Optional[Program]:
        logger.debug(f"Attempting to retrieve program by ID: {program_id}")
        program = self._programs.get(program_id)
        if program:
            logger.info(f"Retrieved program: {program.id}")
        else:
            logger.warning(f"Program with ID: {program_id} not found in database.")
        return program

    async def get_all_programs(self) -> List[Program]:
        logger.debug(f"Retrieving all {len(self._programs)} programs from in-memory database.")
        return list(self._programs.values())

    async def get_best_programs(
        self,
        task_id: str,
        limit: int = 5,
        objective: Literal["correctness", "runtime_ms"] = "correctness",
        sort_order: Literal["asc", "desc"] = "desc",
    ) -> List[Program]:
        logger.info(f"Retrieving best programs for task {task_id}. Limit: {limit}, Objective: {objective}, Order: {sort_order}")
        if not self._programs:
            logger.info("No programs in database to retrieve 'best' from.")
            return []

        all_progs = list(self._programs.values())
                                                                              
                                                                                                                
                                                                                                          
        relevant_progs = all_progs

        def sort_key(p: Program):
            if objective == "correctness":
                return p.fitness_scores.get("correctness", -1.0)
            elif objective == "runtime_ms":
                val = p.fitness_scores.get("runtime_ms", float('inf'))
                                                                                                        
                                                                                       
                                                                                                            
                                                    
                                                                                        
                return -val if sort_order == "desc" else val 
            return 0                                       

                                                                          
        if objective == "correctness":                               
            effective_reverse = (sort_order == "desc")
        elif objective == "runtime_ms":                             
            effective_reverse = (sort_order == "asc")                                                 
        else:
            effective_reverse = False          
        
                                                                   
        if objective == "runtime_ms":
                                                                            
                                                                           
            sorted_programs = sorted(relevant_progs, key=lambda p: p.fitness_scores.get("runtime_ms", float('inf')), reverse=(sort_order == "desc"))
        elif objective == "correctness":
                                                               
                                                                
            sorted_programs = sorted(relevant_progs, key=lambda p: p.fitness_scores.get("correctness", -1.0), reverse=(sort_order == "desc"))
        else:
                                                           
            sorted_programs = sorted(relevant_progs, key=sort_key, reverse=effective_reverse)

        logger.debug(f"Sorted {len(sorted_programs)} programs. Top 3 (if available): {[p.id for p in sorted_programs[:3]]}")
        return sorted_programs[:limit]

    async def get_programs_by_generation(self, generation: int) -> List[Program]:
        logger.debug(f"Retrieving programs for generation: {generation}")
        generation_programs = [p for p in self._programs.values() if p.generation == generation]
        logger.info(f"Found {len(generation_programs)} programs for generation {generation}.")
        return generation_programs

    async def get_programs_for_next_generation(self, task_id: str, generation_size: int) -> List[Program]:
        logger.info(f"Attempting to retrieve {generation_size} programs for next generation for task {task_id}.")
        all_progs = list(self._programs.values())
        if not all_progs:
            logger.warning("No programs in database to select for next generation.")
            return []

        if len(all_progs) <= generation_size:
            logger.debug(f"Returning all {len(all_progs)} programs as it's less than or equal to generation_size {generation_size}.")
            return all_progs
        
        import random
        selected_programs = random.sample(all_progs, generation_size)
        logger.info(f"Selected {len(selected_programs)} random programs for next generation.")
        return selected_programs

    async def count_programs(self) -> int:
        count = len(self._programs)
        logger.debug(f"Total programs in database: {count}")
        return count

    async def clear_database(self) -> None:
        logger.info("Clearing all programs from in-memory database.")
        self._programs.clear()
        logger.info("In-memory database cleared.")

    async def execute(self, *args, **kwargs) -> Any:
        logger.warning("InMemoryDatabaseAgent.execute() called, but this agent uses specific methods for DB operations.")
        raise NotImplementedError("InMemoryDatabaseAgent does not have a generic execute. Use specific methods like save_program, get_program etc.")

    async def get_program_versions(self, program_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Getting version history for program: {program_id}")
        return self._version_history.get(program_id, [])

    async def get_programs_by_regime(self, regime: str) -> List[StrategyProgram]:
        logger.info(f"Getting programs for market regime: {regime}")
        program_ids = self._regime_index.get(regime, [])
        programs = []
        for pid in program_ids:
            program = self._programs.get(pid)
            if program and isinstance(program, StrategyProgram):
                programs.append(program)
        return programs

    async def get_programs_by_parameter(self, param_name: str, param_value: Any) -> List[StrategyProgram]:
        logger.info(f"Getting programs with parameter {param_name}={param_value}")
        program_ids = self._parameter_index.get((param_name, param_value), [])
        programs = []
        for pid in program_ids:
            program = self._programs.get(pid)
            if program and isinstance(program, StrategyProgram):
                programs.append(program)
        return programs

    async def get_programs_by_ast_pattern(self, pattern: str) -> List[Program]:
        logger.info(f"Getting programs with AST pattern: {pattern}")
        program_ids = self._ast_pattern_index.get(pattern, [])
        return [self._programs[pid] for pid in program_ids if pid in self._programs]

    async def get_programs_by_error_type(self, error_type: str) -> List[Program]:
        logger.info(f"Getting programs with error type: {error_type}")
        program_ids = self._error_type_index.get(error_type, [])
        return [self._programs[pid] for pid in program_ids if pid in self._programs]

    async def get_programs_by_performance(self, metric_name: str, metric_value: float) -> List[Program]:
        logger.info(f"Getting programs with {metric_name}={metric_value}")
        program_ids = self._performance_index.get((metric_name, metric_value), [])
        return [self._programs[pid] for pid in program_ids if pid in self._programs]

    async def get_programs_by_api_usage(self, api_call: str) -> List[Program]:
        logger.info(f"Getting programs using API: {api_call}")
        program_ids = self._api_usage_index.get(api_call, [])
        return [self._programs[pid] for pid in program_ids if pid in self._programs]

if __name__ == "__main__":
    import asyncio                                                    
    async def test_db():
        logging.basicConfig(level=logging.DEBUG)
        db = InMemoryDatabaseAgent()

        prog1 = Program(id="prog_001", code="print('hello')", generation=0, fitness_scores={"correctness_score": 0.8, "runtime_ms": 100})
        prog2 = Program(id="prog_002", code="print('world')", generation=0, fitness_scores={"correctness_score": 0.9, "runtime_ms": 50})
        prog3 = Program(id="prog_003", code="print('test')", generation=1, fitness_scores={"correctness_score": 0.85, "runtime_ms": 70})

        await db.save_program(prog1)
        await db.save_program(prog2)
        await db.save_program(prog3)

        retrieved_prog = await db.get_program("prog_001")
        assert retrieved_prog is not None and retrieved_prog.code == "print('hello')"

        all_programs = await db.get_all_programs()
        assert len(all_programs) == 3

        best_correctness = await db.get_best_programs(task_id="test_task", limit=2, objective="correctness", sort_order="desc")
        print(f"Best by correctness (desc): {[p.id for p in best_correctness]}")
        assert len(best_correctness) == 2
        assert best_correctness[0].id == "prog_002"      
        assert best_correctness[1].id == "prog_003"       

        best_runtime_asc = await db.get_best_programs(task_id="test_task", limit=2, objective="runtime_ms", sort_order="asc")
        print(f"Best by runtime (asc): {[p.id for p in best_runtime_asc]}")
        assert len(best_runtime_asc) == 2
        assert best_runtime_asc[0].id == "prog_002"       
        assert best_runtime_asc[1].id == "prog_003"       
        
        best_runtime_desc = await db.get_best_programs(task_id="test_task", limit=2, objective="runtime_ms", sort_order="desc")
        print(f"Best by runtime (desc): {[p.id for p in best_runtime_desc]}")
        assert len(best_runtime_desc) == 2
        assert best_runtime_desc[0].id == "prog_001"        
        assert best_runtime_desc[1].id == "prog_003"       

                                               
        next_gen_programs = await db.get_programs_for_next_generation(task_id="test_task", generation_size=2)
        print(f"Next gen programs (size 2): {[p.id for p in next_gen_programs]}")
        assert len(next_gen_programs) == 2

        next_gen_programs_all = await db.get_programs_for_next_generation(task_id="test_task", generation_size=5)
        print(f"Next gen programs (size 5, all): {[p.id for p in next_gen_programs_all]}")
        assert len(next_gen_programs_all) == 3                              

        gen0_programs = await db.get_programs_by_generation(0)
        assert len(gen0_programs) == 2

        assert await db.count_programs() == 3
        
        await db.clear_database()
        assert await db.count_programs() == 0
        print("InMemoryDatabaseAgent tests passed.")

    asyncio.run(test_db()) 