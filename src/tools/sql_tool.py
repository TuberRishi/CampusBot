import os
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    ListSQLDatabaseTool,
    InfoSQLDatabaseTool,
    QuerySQLDatabaseTool
)

# --- Configuration ---
DB_NAME = "college_events.db"
DB_URI = f"sqlite:///{DB_NAME}"

def get_sql_tools():
    """
    Initializes the SQLDatabase connection and constructs a list of SQL tools.

    This approach manually creates tools to avoid passing the LLM client
    into this module, promoting better separation of concerns.

    Returns:
        list: A list of BaseTool objects for the agent.
    """
    # Check if the database file exists
    if not os.path.exists(DB_NAME):
        raise FileNotFoundError(
            f"Database file not found at '{DB_NAME}'. "
            "Please run 'src/database_setup.py' first."
        )

    # Initialize the SQLDatabase connector
    db = SQLDatabase.from_uri(DB_URI)
    print("SQLDatabase connection initialized.")

    # Manually create a list of tools
    sql_tools = [
        ListSQLDatabaseTool(db=db),
        InfoSQLDatabaseTool(db=db),
        QuerySQLDatabaseTool(db=db)
    ]
    print(f"Manually created {len(sql_tools)} SQL tools.")

    return sql_tools

if __name__ == '__main__':
    # Example of how to use the function to get the tools
    print("Fetching SQL tools...")
    tools = get_sql_tools()
    print(f"\nSuccessfully fetched {len(tools)} tools:")
    for tool in tools:
        print(f"- Tool Name: {tool.name}")
        print(f"  Description: {tool.description}\n")

    # You can also directly get the schema
    db = SQLDatabase.from_uri(DB_URI)
    print("---")
    print("Database Schema:")
    print(db.get_table_info())
