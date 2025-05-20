"""
Main entry point for the AlphaEvolve Pro application.
Orchestrates the different agents and manages the evolutionary loop.
"""
import asyncio
import logging
import sys
import os

                                               
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from task_manager.agent import TaskManagerAgent
from core.interfaces import TaskDefinition
from config import settings
from integrations.deerflow.adapter import DeerFlowAdapter

                   
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE, mode="a")
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting OpenAlpha_Evolve autonomous algorithmic evolution")
    logger.info(f"Configuration: Population Size=20, Generations=10")
    logger.info(f"LLM Models: Pro={settings.PRO_MODEL_NAME}, Flash={settings.FLASH_MODEL_NAME}, Eval={settings.EVALUATION_MODEL}")

    # Add syntax validation requirements to task description
    task = TaskDefinition(
        id="quant_trading_strategy",
        description=(
            "Develop a quantitative trading strategy that meets the following performance criteria: "
            "1) CAGR above 25%, 2) Sharpe ratio greater than 1 (with 5% risk-free rate), "
            "3) Maximum drawdown below 20%, 4) Average profit per trade at least 0.75%, "
            "5) Minimum 100 trades per year. "
            "The strategy should be implemented in QuantConnect's LEAN engine format. "
            "The function should initialize the algorithm, define indicators, and implement "
            "the trading logic including entry/exit rules and position sizing. "
            "The strategy must be backtested over a 15-year period using the provided QuantConnect credentials."
        ),
        function_name_to_evolve="create_trading_strategy",
        input_output_examples=[
            {
                "input": ["SPY", "2010-01-01", "2025-01-01"],
                "output": {
                    "CAGR": 0.28,
                    "SharpeRatio": 1.2,
                    "MaxDrawdown": 0.18,
                    "AverageProfit": 0.008,
                    "AnnualTrades": 105
                }
            },
            {
                "input": ["QQQ", "2010-01-01", "2025-01-01"],
                "output": {
                    "CAGR": 0.30,
                    "SharpeRatio": 1.3,
                    "MaxDrawdown": 0.15,
                    "AverageProfit": 0.009,
                    "AnnualTrades": 110
                }
            }
        ],
        allowed_imports=["QuantConnect", "numpy", "pandas"],
        evaluation_criteria={
            "sharpe_ratio": {"target": 1.0, "weight": 0.35},
            "max_drawdown": {"target": 0.20, "weight": 0.25},
            "total_return": {"target": 0.25, "weight": 0.20},
            "win_rate": {"target": 0.55, "weight": 0.10},
            "profit_factor": {"target": 1.5, "weight": 0.10}
        },
        task_type="strategy",
        backtest_symbol="SPY",
        backtest_start_date="2010-01-01",
        backtest_end_date="2025-01-01",
        initial_capital=100000.0,
        initial_code_prompt=(
            "Initialize a QuantConnect algorithm with the provided credentials. "
            "Implement a mean-reversion strategy with risk management controls. "
            "Include indicators for entry/exit signals and proper position sizing. "
            "Ensure the backtest meets all specified performance metrics. "
            "The code must be valid Python syntax with proper indentation. "
            "Use 4 spaces for indentation. All code blocks must be properly closed. "
            "Avoid common syntax errors like mismatched indentation or missing colons."
        )
    )

                                                              
    task_manager = TaskManagerAgent(
        task_definition=task,
        population_size=20,
        generations=10,
        syntax_validation=True
    )

                                      
    best_programs = await task_manager.execute()

    if best_programs:
        logger.info(f"Evolutionary process completed. Best program(s) found: {len(best_programs)}")
        for i, program in enumerate(best_programs):
            logger.info(f"Final Best Program {i+1} ID: {program.id}")
            logger.info(f"Final Best Program {i+1} Fitness: {program.fitness_scores}")
            logger.info(f"Final Best Program {i+1} Code:\n{program.code}")
    else:
        logger.info("Evolutionary process completed, but no suitable programs were found.")

    logger.info("OpenAlpha_Evolve run finished.")

if __name__ == "__main__":
    asyncio.run(main())
