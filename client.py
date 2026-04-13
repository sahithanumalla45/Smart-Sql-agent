import asyncio
from agent_core import SQLAgent

# -------------------------------
# Terminal CLI Debug / Dev Client
# -------------------------------
async def main():
    agent = SQLAgent()
    await agent.setup()

    print("🧠 SQL Agent CLI Debugger")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("SQL-Agent > ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Run agent
        response = await agent.run(user_input)
        print("\n[Agent Response]")
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
