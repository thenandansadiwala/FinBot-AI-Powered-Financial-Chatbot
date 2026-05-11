import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from app.agent.state import AgentState
from app.agent.tools import get_financial_metrics_sql, search_fund_strategies_vector
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class IntentSchema(BaseModel):
    query_intent: str = Field(
        description="Classify the user's intent as one of: 'sql_filter', 'vector_search', 'general_chat'"
    )
    detected_tickers: list[str] = Field(
        default_factory=list,
        description="Extract any fund ticker symbols mentioned in the user's query (e.g., ['SPY', 'QQQ']). Return empty list if none."
    )

async def intent_classifier_node(state: AgentState) -> Dict[str, Any]:
    """Classifies the user intent and updates the query_intent state."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    logger.info("Classifying intent...")
    prompt = (
        "Analyze the user's financial query and classify the intent:\n"
        "- 'sql_filter': Use this if the query asks for specific financial metrics, data points, fund size, expense ratio, NAV, or filtering (e.g., 'What is the expense ratio of SPY?', 'Show me funds larger than 1000 Cr').\n"
        "- 'vector_search': Use this if the query asks about thematic strategies, qualitative descriptions, or concepts (e.g., 'sustainable funds', 'AI focused strategies').\n"
        "- 'general_chat': Use this only for greetings, general conversation, or queries completely unrelated to finding specific funds or metrics.\n\n"
        f"Query: '{last_message}'"
    )
    
    llm = AzureChatOpenAI(azure_deployment=settings.LLM_MODEL, api_version="2024-02-01", temperature=0)
    intent_classifier = llm.with_structured_output(IntentSchema)
    result = await intent_classifier.ainvoke(prompt)
    
    intent = result.query_intent
    detected_tickers = result.detected_tickers
    
    # Merge new tickers into existing context
    current_symbols = state.get("working_ticker_symbols", [])
    updated_symbols = list(set(current_symbols + [t.upper() for t in detected_tickers]))
    
    logger.info(f"Classified intent as: {intent}. Extracted tickers: {detected_tickers}")
    return {"query_intent": intent, "working_ticker_symbols": updated_symbols}


async def sql_execution_node(state: AgentState) -> Dict[str, Any]:
    """Triggers the SQL tool if the intent requires hard metrics/filtering."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    logger.info("Executing SQL node...")
    sql_result = await get_financial_metrics_sql.ainvoke(last_message)
    
    # Inject the SQL result into the conversation memory as a system context message
    context_msg = SystemMessage(content=f"Data retrieved from SQL database:\n{sql_result}")
    return {"messages": [context_msg]}


async def vector_execution_node(state: AgentState) -> Dict[str, Any]:
    """Triggers the Vector tool if the intent requires thematic searching."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    logger.info("Executing Vector Search node...")
    vector_result = await search_fund_strategies_vector.ainvoke(last_message)
    
    # Inject the Vector result into the conversation memory as a system context message
    context_msg = SystemMessage(content=f"Data retrieved from Vector Search (Fund Strategies):\n{vector_result}")
    return {"messages": [context_msg]}


async def generate_response_node(state: AgentState) -> Dict[str, Any]:
    """Takes the tool outputs and formats them into a clean, structured natural language response."""
    messages = state["messages"]
    
    logger.info("Generating final response...")
    
    system_prompt = (
        "You are an expert AI financial assistant. Using the conversation history and the context data provided by our internal tools, "
        "answer the user's query comprehensively and accurately in a clean, structured natural language format.\n"
        "ALWAYS use Markdown formatting for your responses. For comparisons, lists of funds, or multiple data points, you MUST use Markdown tables to ensure readability.\n"
        "CRITICAL INSTRUCTION: You MUST strictly use the data provided in the tool execution context. "
        "Trust the database context absolutely, even if it contradicts your pre-trained knowledge or seems incorrect. "
        "Do not correct or dispute the database values. If you are lacking data, say so explicitly.\n"
        "GUARDRAIL INSTRUCTION: You are strictly a financial data assistant. If the user's query is completely unrelated to finance, investments, funds, or ETFs, you MUST politely decline to answer and remind them that you are exclusively a financial chatbot. You may reply to basic pleasantries, but firmly pivot back to finance."
    )
    
    # Prepend the overarching system directive to the active messages payload
    generation_messages = [SystemMessage(content=system_prompt)] + messages
    
    llm = AzureChatOpenAI(azure_deployment=settings.LLM_MODEL, api_version="2024-02-01", temperature=0)
    response = await llm.ainvoke(generation_messages)
    return {"messages": [response]}
