import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import os # Import os for patching getenv

from OpenAlpha_Evolve.evaluator_agent.agent import EvaluatorAgent
from OpenAlpha_Evolve.core.interfaces import TaskDefinition

@pytest.mark.asyncio
async def test_get_market_regime_instantiates_async_memory_client():
    mock_task_definition = TaskDefinition(id="test_task", description="Test task")

    mock_mem0_instance = AsyncMock()
    mock_mem0_instance.search = AsyncMock(return_value={"results": []})

    # Patch os.getenv to simulate MEM0_API_KEY being set
    # The mem0 SDK (AsyncMemoryClient) likely checks os.getenv("MEM0_API_KEY") internally.
    # Patching os.environ ensures that this check passes.
    with patch.dict(os.environ, {'MEM0_API_KEY': 'test_key'}):
        # Patch AsyncMemoryClient itself to ensure it's called and to control its behavior.
        # This path should work because AsyncMemoryClient is imported at the module level
        # in OpenAlpha_Evolve.evaluator_agent.agent.
        with patch('OpenAlpha_Evolve.evaluator_agent.agent.AsyncMemoryClient', return_value=mock_mem0_instance) as mock_async_mem_client_constructor:
            agent = EvaluatorAgent(task_definition=mock_task_definition)
            await agent._get_market_regime()
            
            mock_async_mem_client_constructor.assert_called_once_with() # Check it's called
            mock_mem0_instance.search.assert_called_once_with(
                query="current market regime",
                limit=3,
                user_id="market_regime_analyzer"
            )

import os # Ensure os is imported at the top of the file if not already
# (pytest, asyncio, TaskDefinition, EvaluatorAgent should already be imported)

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("MEM0_API_KEY"), reason="MEM0_API_KEY environment variable not set for real API test")
async def test_get_market_regime_with_real_api_key_integration():
    """
    Tests the _get_market_regime method's interaction with the live Mem0 service.
    This test requires the MEM0_API_KEY environment variable to be set.
    It does not mock AsyncMemoryClient and expects a real connection.
    """
    mock_task_definition = TaskDefinition(id="test_task_real_api", description="Test task for real API")
    agent = EvaluatorAgent(task_definition=mock_task_definition)

    # Ensure MEM0_API_KEY is actually available for the real client,
    # the skipif decorator handles skipping, but an explicit check can be illustrative
    # or used if the client has its own way of indicating a missing key that we want to bypass for this test's purpose.
    # However, mem0's AsyncMemoryClient is expected to raise an error if the key is missing,
    # which is what we want to avoid if skipif is not triggered for some reason or if we wanted to test that error.
    # For this test, we assume skipif works and the key is present if the test runs.

    print(f"Attempting to run test_get_market_regime_with_real_api_key_integration with MEM0_API_KEY='{os.getenv('MEM0_API_KEY')[:5]}...'") # Log safely

    try:
        result = await agent._get_market_regime()

        assert isinstance(result, dict), "Result should be a dictionary"
        assert "regime" in result, "Result dictionary should contain a 'regime' key"
        assert "confidence" in result, "Result dictionary should contain a 'confidence' key"
        # We don't assert specific values for 'regime' or 'confidence' as they depend on the live service state.
        print(f"Successfully received result from mem0: {result}")

    except Exception as e:
        # If an exception occurs, fail the test with information.
        # This could be due to network issues, real API errors, unexpected response format, etc.
        pytest.fail(f"_get_market_regime with real API key failed: {type(e).__name__}: {e}")
