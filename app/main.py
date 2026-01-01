from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from graph import app_graph

app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    session_id: str
    history: Optional[List[str]] = []

@app.post("/query")
async def query_db(req: ChatRequest):
    inputs = {
        "question": req.query,
        "chat_history": req.history,
        "retry_count": 0,
        "schema": "",
        "sql_query": "",
        "result": "",
        "error": None
    }
    
    final_state = await app_graph.ainvoke(inputs)
    
    if final_state.get("error") and final_state["retry_count"] >= 3:
        return {
            "response": f"I encountered an error: {final_state['error']}",
            "sql_generated": final_state["sql_query"]
        }
        
    return {
        "response": final_state["result"],
        "sql_used": final_state["sql_query"]
    }