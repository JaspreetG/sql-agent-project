import os
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from tools import get_schema, run_query

# Define State
class GraphState(TypedDict):
    question: str
    chat_history: List[str]
    schema: str
    sql_query: str
    result: str
    error: Optional[str]
    retry_count: int

# --- DUAL MODEL SETUP ---
# Model 1: The Coder (Strict, SQL-specialized)
llm_sql = ChatOllama(model="sqlcoder:7b", base_url=os.getenv("OLLAMA_BASE_URL"), temperature=0)

# Model 2: The Speaker (Chatty, Llama3)
llm_chat = ChatOllama(model="llama3", base_url=os.getenv("OLLAMA_BASE_URL"), temperature=0.7)

# Nodes
def fetch_schema_node(state: GraphState):
    return {"schema": get_schema(), "retry_count": 0}

def generate_sql_node(state: GraphState):
    # Specialized Prompt for SQLCoder
    prompt = f"""### Task
Generate a SQL query to answer [QUESTION]{state['question']}[/QUESTION]

### Database Schema
The query will run on a database with the following schema:
{state['schema']}

### Answer
Given the database schema, here is the SQL query that [QUESTION]{state['question']}[/QUESTION]
[SQL]
"""
    if state.get("error"):
        prompt += f"\n/* PREVIOUS ERROR: {state['error']} - FIX THIS */"

    response = llm_sql.invoke([HumanMessage(content=prompt)])
    
    # Cleaning output strictly
    sql = response.content.replace("```sql", "").replace("```", "").strip()
    return {"sql_query": sql}

def execute_sql_node(state: GraphState):
    result = run_query(state['sql_query'])
    if "ERROR:" in str(result):
        return {"error": result, "retry_count": state["retry_count"] + 1}
    return {"result": str(result), "error": None}

def summarize_node(state: GraphState):
    # Use Llama3 for natural language summary
    prompt = f"""
    User asked: {state['question']}
    Data retrieved: {state['result']}
    
    Please provide a concise, friendly summary of this data.
    """
    response = llm_chat.invoke([HumanMessage(content=prompt)])
    return {"result": response.content}

def should_continue(state: GraphState):
    if state["error"]:
        return "retry" if state["retry_count"] < 3 else "end"
    return "success"

# Build Workflow
workflow = StateGraph(GraphState)
workflow.add_node("get_schema", fetch_schema_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("summarize", summarize_node)

workflow.set_entry_point("get_schema")
workflow.add_edge("get_schema", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    should_continue,
    {
        "retry": "generate_sql",
        "success": "summarize",
        "end": END
    }
)
workflow.add_edge("summarize", END)

app_graph = workflow.compile()