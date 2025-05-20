import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, call
from OpenAlpha_Evolve.task_manager.agent import TaskManagerAgent
from OpenAlpha_Evolve.core.interfaces import TaskDefinition, Program
from OpenAlpha_Evolve.database_agent.agent import InMemoryDatabaseAgent
from OpenAlpha_Evolve.code_generator.agent import CodeGeneratorAgent
from OpenAlpha_Evolve.prompt_designer.agent import PromptDesignerAgent

@pytest.mark.asyncio
async def test_initialize_population_workflow():
    # 1. Set up the TaskDefinition
    sample_task_definition = TaskDefinition(
        id="test_task_001", 
        description="Create a function that prints numbers 1 to 10. Criteria: Function must print numbers from 1 to 10. Must be a Python function.", # Incorporated criteria into description
        # criteria field removed as it's not part of TaskDefinition model.
        # evaluation_criteria could be used if criteria were a Dict.
        # dependencies=[], # Removed dependencies as it's not a valid field
        # deadline=None, # Removed deadline as it's not a valid field
        # difficulty=1, # Removed difficulty as it's not a valid field
        # initial_prompt_override=None # Removed initial_prompt_override as it's not a valid field
        # Note: initial_code_prompt IS a valid field, but was not used here.
    )

    # 2. Instantiate TaskManagerAgent
    population_size = 2
    task_manager = TaskManagerAgent(
        task_definition=sample_task_definition,
        population_size=population_size,
        # syntax_validation=False, # generate_code in TaskManagerAgent doesn't take this param directly
        # Instead, we will ensure the mock for generate_code doesn't raise syntax errors.
        # The CodeGeneratorAgent within TaskManagerAgent will have its own syntax_validation setting,
        # which is True by default. For this integration test, we are mocking generate_code's output directly.
    )

    # 3. Mock dependencies on the TaskManager's instances
    # Mock PromptDesignerAgent
    test_prompt_value = "Design a Python function to print numbers 1 to 10"
    # task_manager.prompt_designer is an instance of PromptDesignerAgent
    task_manager.prompt_designer.design_initial_prompt = MagicMock(return_value=test_prompt_value)

    # Mock CodeGeneratorAgent
    generated_code_1 = "def print_numbers_v1():\n    for i in range(1, 11):\n        print(i)"
    generated_code_2 = "def print_numbers_v2():\n    # A slightly different version\n    for i in range(1, 11):\n        print(f'Number: {i}')"
    # task_manager.code_generator is an instance of CodeGeneratorAgent
    task_manager.code_generator.generate_code = AsyncMock(side_effect=[generated_code_1, generated_code_2])
    
    # The InMemoryDatabaseAgent is created internally by TaskManagerAgent.
    # We will access task_manager.database to check the state after execution.

    # 4. Execute the initialize_population method
    await task_manager.initialize_population()

    # 5. Verify calls to mocks
    # Verify PromptDesignerAgent calls
    assert task_manager.prompt_designer.design_initial_prompt.call_count == population_size
    # Since the prompt is the same for all initial population members for this task
    # Corrected: design_initial_prompt in PromptDesignerAgent takes no arguments
    task_manager.prompt_designer.design_initial_prompt.assert_called_with()
    
    # Verify CodeGeneratorAgent calls
    assert task_manager.code_generator.generate_code.call_count == population_size
    expected_calls_to_generate_code = [
        call(
            prompt=test_prompt_value,
            temperature=0.8, # Actual value from TaskManagerAgent.initialize_population
            syntax_validation=False  # Actual value from TaskManagerAgent (default for self.syntax_validation)
            # parent_code, max_length, output_format are not explicitly passed by initialize_population,
            # so they are not included in the expected call signature for assert_has_calls.
        ),
        call(
            prompt=test_prompt_value, 
            temperature=0.8,
            syntax_validation=False
        )
    ]
    task_manager.code_generator.generate_code.assert_has_calls(expected_calls_to_generate_code)

    # 6. Verify database state
    all_programs = await task_manager.database.get_all_programs()
    assert len(all_programs) == population_size

    saved_codes = [p.code for p in all_programs]
    assert generated_code_1 in saved_codes
    assert generated_code_2 in saved_codes

    for program in all_programs:
        assert program.generation == 0
        assert program.status == "unevaluated"
        assert program.fitness_score is None # Initially no fitness score
        assert program.parent_program_id is None # Initial population has no parents
        assert program.llm_prompt == test_prompt_value # Prompt used for generation
        assert program.task_id == sample_task_definition.id # Changed to .id
        assert program.description.startswith(f"Initial program for task {sample_task_definition.id}") # Changed to .id

    # Check that program_ids are unique (basic check)
    program_ids = [p.id for p in all_programs] # Changed to .id
    assert len(program_ids) == len(set(program_ids))

    print(f"Integration test for population initialization completed successfully for {population_size} programs.")

# To run this test, you would typically use pytest from your terminal:
# pytest OpenAlpha_Evolve/tests/integration/test_population_initialization.py
# ```
# The triple backticks above were causing a syntax error.
# They have been commented out.
