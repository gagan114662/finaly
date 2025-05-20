import asyncio
import logging
from OpenAlpha_Evolve.database_agent.agent import InMemoryDatabaseAgent
from OpenAlpha_Evolve.core.interfaces import Program

async def test_database():
    logging.basicConfig(level=logging.INFO)
    db = InMemoryDatabaseAgent()
    
    # Create and save a test program
    prog = Program(
        id="test_prog",
        code="print('Hello World')",
        generation=0,
        fitness_scores={"correctness": 0.9}
    )
    await db.save_program(prog)
    print("Saved program successfully")
    
    # Retrieve and verify
    retrieved = await db.get_program("test_prog")
    if retrieved:
        print(f"Retrieved program code: {retrieved.code}")
        print(f"Program fitness: {retrieved.fitness_scores}")
    else:
        print("Failed to retrieve program")

if __name__ == "__main__":
    asyncio.run(test_database())