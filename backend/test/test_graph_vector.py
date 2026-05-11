import sys
import os
import asyncio

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load config mapping early
from app.core.config import settings

from langchain_openai import AzureOpenAIEmbeddings
from app.db.database import async_session_maker
from app.db.models import FundEmbedding
from sqlalchemy import select
from langchain_core.messages import HumanMessage
from app.agent.graph import app

async def backfill_embeddings():
    print("--- Part 1: Backfilling Real Embeddings ---")
    embeddings_model = AzureOpenAIEmbeddings(
        azure_deployment=settings.EMBEDDING_MODEL, 
        api_version="2024-02-01"
    )
    
    async with async_session_maker() as session:
        # Fetch all existing embeddings
        result = await session.execute(select(FundEmbedding))
        embeddings_records = result.scalars().all()
        
        updated_count = 0
        for entry in embeddings_records:
            print(f"Generating real Azure OpenAI embedding for {entry.ticker_symbol}...")
            # We call the embedding model directly on the context_text (longBusinessSummary)
            real_vector = await embeddings_model.aembed_query(entry.context_text)
            
            entry.embedding = real_vector
            updated_count += 1
            
        if updated_count > 0:
            await session.commit()
            print(f"Successfully committed {updated_count} real fund embeddings to the database.\n")
        else:
            print("No embeddings found to update.\n")

async def test_vector_graph():
    print("--- Part 2: Testing Vector Graph Execution ---")
    
    query = "Which of our funds are best suited for tracking the broader technology sector and large-cap growth?"
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "working_ticker_symbols": [],
        "query_intent": ""
    }
    
    print(f"Initial Query: '{query}'")
    print("-" * 50)
    
    # We use astream() instead of ainvoke() so we can print the events step-by-step
    async for event in app.astream(initial_state):
        for node_name, state_update in event.items():
            print(f">>> Execution Node: {node_name} <<<")
            
            if "query_intent" in state_update:
                print(f" -> Classified Intent: {state_update['query_intent']}")
                
            if "messages" in state_update:
                for msg in state_update["messages"]:
                    print(f" -> Output: {msg.content[:800]}...\n") 
                    
            print("-" * 50)
            
    print("\n--- Execution Finished ---")

async def main():
    await backfill_embeddings()
    await test_vector_graph()

if __name__ == "__main__":
    asyncio.run(main())
