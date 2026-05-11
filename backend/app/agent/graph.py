from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    intent_classifier_node,
    sql_execution_node,
    vector_execution_node,
    generate_response_node
)

def route_intent(state: AgentState) -> str:
    """
    Conditional edge router that directs traffic based on the query_intent.
    """
    intent = state.get("query_intent")
    if intent == "sql_filter":
        return "sql_execution"
    elif intent == "vector_search":
        return "vector_execution"
    else:
        # Default fallback for "general_chat" or unmapped intents
        return "generate_response"

# 1. Initialize StateGraph
workflow = StateGraph(AgentState)

# 2. Add standard execution nodes
workflow.add_node("intent_classifier", intent_classifier_node)
workflow.add_node("sql_execution", sql_execution_node)
workflow.add_node("vector_execution", vector_execution_node)
workflow.add_node("generate_response", generate_response_node)

# 3. Define Entry Point
workflow.set_entry_point("intent_classifier")

# 4. Define Edges & Routing
workflow.add_conditional_edges(
    "intent_classifier",
    route_intent,
    {
        "sql_execution": "sql_execution",
        "vector_execution": "vector_execution",
        "generate_response": "generate_response"
    }
)

# Tool execution nodes map directly back to the generation node
workflow.add_edge("sql_execution", "generate_response")
workflow.add_edge("vector_execution", "generate_response")

# Terminate after final response generation
workflow.add_edge("generate_response", END)

# 5. Compile the LangGraph
app = workflow.compile()
