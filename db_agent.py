from pydantic_ai import Agent

# from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.mcp import MCPServerHTTP

#
from dotenv import load_dotenv
import os

load_dotenv()
# logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

# Get the API key and create a new environment dict that includes it
# api_key = os.getenv("DOCKETBIRD_API_KEY")
# env = os.environ.copy()  # Make a copy of the current environment

# Create the MCP server with the environment variables
# docketbird_server = MCPServerStdio(
#     "uv",
#     ["run", "docketbird_mcp.py", "--transport", "stdio"],
#     env=env,  # Pass the environment to the subprocess
# )

docketbird_server = MCPServerHTTP(url="http://165.227.221.151:8040/sse")

agent = Agent("openai:gpt-4o", instrument=False, mcp_servers=[docketbird_server])
# agent = Agent("openai:gpt-4o", instrument=True, mcp_servers=[docketbird_server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run(POC_PROMPT)
        while True:
            print(f"\n{result.data}")
            user_input = input("\n> ")
            result = await agent.run(user_input, message_history=result.new_messages())


if __name__ == "__main__":
    import asyncio

    POC_PROMPT = "What are the case details for txnd-3:2007-cv-01697?"
    asyncio.run(main())
