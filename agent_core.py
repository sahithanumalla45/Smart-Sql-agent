import os
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context

# -------------------------------------------------
# ENV + LLM
# ----------------------------------------a---------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=api_key,
)

Settings.llm = llm

# -------------------------------------------------
# SYSTEM PROMPT (yours, slightly tightened)
# -------------------------------------------------
SYSTEM_PROMPT = """
You are an AI assistant for SQL tool calling.

Rules:
1. ALWAYS use tools for database operations.
2. Support CREATE, INSERT, SELECT, UPDATE, DELETE,
   DROP, TRUNCATE, ALTER.
3. If input is ambiguous, ask ONE clarification question.
4. Format SELECT output as SQL table.
5.create er diagrams if asked and display the er diagram image
"""

# -------------------------------------------------
# REUSABLE AGENT
# -------------------------------------------------
class SQLAgent:
    def __init__(self):
        self.agent = None
        self.ctx = None

    async def setup(self):
        mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
        mcp_tools = McpToolSpec(client=mcp_client)

        tools = await mcp_tools.to_tool_list_async()

        self.agent = FunctionAgent(
            name="SQL-Agent",
            description="Universal SQL Agent",
            tools=tools,
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
        )

        self.ctx = Context(self.agent)

    async def run(self, user_input: str) -> str:
        handler = self.agent.run(user_input, ctx=self.ctx)
        response = await handler
        return str(response)
