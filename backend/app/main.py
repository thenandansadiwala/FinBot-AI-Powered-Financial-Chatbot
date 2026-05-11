import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

# Ensure absolute imports work if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.core.logger import setup_logger
from app.agent.graph import app as agent_app
from langchain_core.messages import HumanMessage

logger = setup_logger(__name__)

app = FastAPI(title="Financial Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    working_ticker_symbols: List[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str
    updated_symbols: List[str]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received API chat request. Message length: {len(request.message)} chars. Active Context: {request.working_ticker_symbols}")
    try:
        # Construct the initial AgentState
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "working_ticker_symbols": request.working_ticker_symbols,
            "query_intent": ""
        }
        
        # Invoke the LangGraph agent asynchronously
        logger.info("Invoking LangGraph agent pipeline...")
        final_state = await agent_app.ainvoke(initial_state)
        logger.info("LangGraph agent execution completed successfully.")
        
        # Extract the final message from the conversation memory
        final_message = final_state["messages"][-1].content
        
        # Extract the updated tracking context
        updated_symbols = final_state.get("working_ticker_symbols", [])
        
        logger.info(f"Returning response. Updated context: {updated_symbols}")
        return ChatResponse(
            response=final_message,
            updated_symbols=updated_symbols
        )
    except Exception as e:
        logger.error(f"Critical error during LangGraph execution: {str(e)}", exc_info=True)
        return ChatResponse(
            response="I'm sorry, I encountered an internal error while connecting to the database or language model. Please check the logs.",
            updated_symbols=request.working_ticker_symbols
        )

if __name__ == "__main__":
    # We specify "app.main:app" to allow uvicorn's auto-reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
