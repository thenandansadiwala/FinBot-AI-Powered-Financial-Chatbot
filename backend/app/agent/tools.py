from typing import Optional
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from sqlalchemy import select

from app.core.config import settings
from app.db.database import async_session_maker
from app.db.models import FundEmbedding
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# --- 1. SQL Agent Tool ---
db = SQLDatabase.from_uri(
    settings.SYNC_DB_URL,
    include_tables=["funds_master", "amc_profiles", "fund_categories", "nav_history"]
)

@tool
async def get_financial_metrics_sql(query: str) -> str:
    """
    Executes a SQL query against the financial database to retrieve hard metrics or filter data.
    Input should be a natural language question about financial metrics, fund size, or historical NAV.
    """
    logger.info(f"Initializing SQL Agent for query: '{query}'")
    # Create the LLM and executor locally to bind to the current asyncio loop!
    llm = AzureChatOpenAI(azure_deployment=settings.LLM_MODEL, api_version="2024-02-01", temperature=0)
    sql_agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        prefix=(
            "You are a financial data expert. You have access to a SQL database with the following tables: "
            "funds_master, amc_profiles, fund_categories, and nav_history. "
            "Always use ticker_symbol for joining funds_master and nav_history. "
            "For amc_profiles use amc_id. For fund_categories use category_id."
        )
    )
    
    # Invoking the pre-built SQL agent
    logger.info("Executing SQL Agent chain...")
    try:
        response = await sql_agent_executor.ainvoke({"input": query})
        logger.info("SQL Agent executed successfully.")
        return response["output"]
    except Exception as e:
        logger.error(f"SQL Agent encountered an error: {str(e)}", exc_info=True)
        return "An error occurred while querying the database."

@tool
async def search_fund_strategies_vector(query: str) -> str:
    """
    Performs a vector similarity search on the fund_embeddings table to find funds matching a thematic 
    strategy or qualitative description (e.g., 'sustainable funds', 'tech focused').
    """
    logger.info(f"Executing Vector Search tool for query: '{query}'")
    
    # Create the embeddings model locally to bind to the current asyncio loop
    embeddings_model = AzureOpenAIEmbeddings(azure_deployment=settings.EMBEDDING_MODEL, api_version="2024-02-01")
    
    # Generate vector for user query
    try:
        query_vector = await embeddings_model.aembed_query(query)
    except Exception as e:
        logger.error(f"Failed to generate query embeddings: {str(e)}", exc_info=True)
        return "An error occurred during vector generation."
    
    async with async_session_maker() as session:
        # pgvector uses the cosine_distance method mapped to <=> operator
        stmt = (
            select(FundEmbedding)
            .order_by(FundEmbedding.embedding.cosine_distance(query_vector))
            .limit(3)
        )
        result = await session.execute(stmt)
        closest_funds = result.scalars().all()
        
        if not closest_funds:
            logger.info("Vector Search returned 0 results.")
            return "No relevant fund strategies found."
            
        logger.info(f"Vector Search retrieved {len(closest_funds)} funds.")
            
        context_parts = []
        for fund in closest_funds:
            context_parts.append(f"Ticker: {fund.ticker_symbol}\nContext: {fund.context_text}")
            
        return "\n\n".join(context_parts)
