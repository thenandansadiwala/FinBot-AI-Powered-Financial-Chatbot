from typing import List, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state structure for the LangGraph agent.
    - messages: Holds the conversation history (BaseMessage objects). 
      The 'add_messages' reducer ensures new messages are appended, not overwritten.
    - working_ticker_symbols: A list of active ticker symbols being analyzed or filtered.
    - query_intent: The classification of the user's intent.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    working_ticker_symbols: List[str]
    query_intent: str
