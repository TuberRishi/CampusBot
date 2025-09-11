from langgraph.graph import StateGraph, END
from .state import AgentState
from .chains import (
    detect_language_chain,
    refine_query_chain,
    rag_chain,
    sql_chain,
    external_help_chain,
    general_qa_chain,
    translate_client, # Import the client for the final translation step
)
from .router import query_router

# --- Graph Nodes ---

def detect_language_node(state: AgentState) -> dict:
    """Node to detect the language of the query."""
    print("---NODE: DETECT LANGUAGE---")
    return detect_language_chain(state)

def refine_query_node(state: AgentState) -> dict:
    """Node to refine the query."""
    print("---NODE: REFINE QUERY---")
    return refine_query_chain.invoke(state)

def route_query_node(state: AgentState) -> dict:
    """Node to decide which tool to use."""
    print("---NODE: ROUTE QUERY---")
    route = query_router.invoke(state)
    print(f"---ROUTE: {route.datasource}---")
    return {"source": route.datasource}

def run_rag_node(state: AgentState) -> dict:
    """Node to run the RAG chain."""
    print("---NODE: RUN RAG---")
    return rag_chain.invoke(state)

def run_sql_node(state: AgentState) -> dict:
    """Node to run the SQL chain."""
    print("---NODE: RUN SQL---")
    # sql_chain is a regular function, not a Runnable, so we call it directly
    return sql_chain(state)

def run_help_node(state: AgentState) -> dict:
    """Node to run the External Help chain."""
    print("---NODE: RUN EXTERNAL HELP---")
    return external_help_chain.invoke(state)

def run_general_node(state: AgentState) -> dict:
    """Node to run the General QA chain."""
    print("---NODE: RUN GENERAL QA---")
    return general_qa_chain.invoke(state)

def translate_answer_node(state: AgentState) -> dict:
    """Node to translate the final answer back to the original language."""
    print("---NODE: TRANSLATE FINAL ANSWER---")
    original_lang = state.get("language", "en")
    english_answer = state.get("answer", "")

    if not translate_client or not english_answer:
        return {} # Return no changes if client or answer is missing

    try:
        result = translate_client.translate(english_answer, target_language=original_lang)
        translated_answer = result["translatedText"]
        print(f"---TRANSLATED ANSWER to {original_lang}: {translated_answer}---")
        return {"answer": translated_answer}
    except Exception as e:
        print(f"---ERROR during final translation: {e}---")
        return {} # Return no changes on error

# --- Conditional Edges ---

def where_to_go(state: AgentState) -> str:
    """Conditional edge to decide the next step after routing."""
    return state.get("source", "General")

def after_tool_run(state: AgentState) -> str:
    """Conditional edge to decide if final translation is needed."""
    if state.get("language", "en") != "en":
        return "translate_answer"
    else:
        return END

# --- Build the Graph ---

# Create a new state graph
workflow = StateGraph(AgentState)

# Add all the nodes to the graph
workflow.add_node("detect_language", detect_language_node)
workflow.add_node("refine_query", refine_query_node)
workflow.add_node("route_query", route_query_node)
workflow.add_node("RAG", run_rag_node)
workflow.add_node("SQL", run_sql_node)
workflow.add_node("External Help", run_help_node)
workflow.add_node("General", run_general_node)
workflow.add_node("translate_answer", translate_answer_node)

# Set the entry point of the graph
workflow.set_entry_point("detect_language")

# Add edges connecting the nodes
workflow.add_edge("detect_language", "refine_query")
workflow.add_edge("refine_query", "route_query")

# The routing conditional edge
workflow.add_conditional_edges(
    "route_query",
    where_to_go,
    {
        "RAG": "RAG",
        "SQL": "SQL",
        "External Help": "External Help",
        "General": "General",
    },
)

# After running a tool, decide whether to translate or end
workflow.add_conditional_edges("RAG", after_tool_run)
workflow.add_conditional_edges("SQL", after_tool_run)
workflow.add_conditional_edges("External Help", after_tool_run)
workflow.add_conditional_edges("General", after_tool_run)

# The final translation node always ends the process
workflow.add_edge("translate_answer", END)

# Compile the graph into a runnable app
app = workflow.compile()

print("LangGraph compiled successfully!")
