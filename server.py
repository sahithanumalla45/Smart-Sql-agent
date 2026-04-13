import sqlite3
from fastmcp import FastMCP
from typing import Any, Dict, List

# -------------------------------------------------
# MCP SERVER INIT
# -------------------------------------------------
mcp = FastMCP("Universal SQLite MCP Server")

DB_PATH = "demo.db"

# -------------------------------------------------
# DATABASE INIT
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.commit()
    conn.close()
    print("[DEBUG] SQLite database initialized.")

# -------------------------------------------------
# HELPER: EXECUTE SQL
# -------------------------------------------------
def execute_sql_internal(query: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        # SELECT queries
        if query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            return {
                "type": "select",
                "columns": columns,
                "rows": rows,
            }

        # Non-SELECT queries
        conn.commit()
        return {
            "type": "mutation",
            "rows_affected": cursor.rowcount,
            "status": "success",
        }

    except Exception as e:
        return {
            "type": "error",
            "error": str(e),
        }

    finally:
        conn.close()

# -------------------------------------------------
# MCP TOOL: EXECUTE SQL
# -------------------------------------------------
@mcp.tool()
def execute_sql(query: str) -> Dict[str, Any]:
    """
    Execute ANY SQL statement.
    Supports SELECT, INSERT, UPDATE, DELETE,
    CREATE, DROP, TRUNCATE, ALTER, etc.
    """
    print(f"[SQL] {query}")
    return execute_sql_internal(query)

# -------------------------------------------------
# MCP TOOL: SHOW TABLES (QUALITY OF LIFE)
# -------------------------------------------------
@mcp.tool()
def show_tables() -> List[str]:
    """Return a list of all tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# -------------------------------------------------
# MCP TOOL: DESCRIBE TABLE
# -------------------------------------------------
@mcp.tool()
def describe_table(table_name: str) -> List[Dict[str, Any]]:
    """Return schema information for a table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")

    schema = [
        {
            "cid": row[0],
            "name": row[1],
            "type": row[2],
            "not_null": bool(row[3]),
            "default": row[4],
            "primary_key": bool(row[5]),
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return schema

# -------------------------------------------------
# SERVER START
# -------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("🚀 Starting Universal SQLite MCP Server on port 8000...")
    mcp.run(transport="sse", port=8000)
