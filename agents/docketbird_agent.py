from pydantic_ai import Agent

from pydantic_ai.mcp import MCPServerStdio, MCPServerHTTP

import logfire
from dotenv import load_dotenv
import os
import sys
from termcolor import colored

load_dotenv()
# logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

# Check if OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    print(colored("Error: OPENAI_API_KEY environment variable is not set.", "red"))
    print(colored("Please set this environment variable and try again.", "red"))
    print(colored("Example: export OPENAI_API_KEY=your_api_key_here", "yellow"))
    sys.exit(1)

# Get the API key and create a new environment dict that includes it
api_key = os.getenv("DOCKETBIRD_API_KEY")
env = os.environ.copy()  # Make a copy of the current environment

# Create the MCP server with the environment variables
# docketbird_server = MCPServerStdio(
#     "uv",
#     ["run", "docketbird_mcp/docketbird_mcp.py", "--transport", "stdio"],
#     env=env,  # Pass the environment to the subprocess
# )

docketbird_server = MCPServerHTTP(url="http://165.227.221.151:8040/sse")

agent = Agent("openai:gpt-4.1", instrument=False, mcp_servers=[docketbird_server])


async def main():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ██████╗  ██████╗  ██████╗██╗  ██╗███████╗████████╗     ║
    ║   ██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝     ║
    ║   ██║  ██║██║   ██║██║     █████╔╝ █████╗     ██║        ║
    ║   ██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝     ██║        ║
    ║   ██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗   ██║        ║
    ║   ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝        ║
    ║                                                           ║
    ║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗            ║
    ║   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝           ║
    ║   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║              ║
    ║   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║              ║
    ║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║              ║
    ║   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(colored(banner, "cyan"))
    print(colored("Welcome to Docket Agent - Your Legal Research Assistant", "cyan"))
    print()
    print(colored("✓ Find cases with natural language queries", "green"))
    print(colored("✓ Retrieve case details and documents from federal courts", "green"))
    print(
        colored("✓ Download documents to case-specific folders automatically", "green")
    )
    print(colored("✓ Save and restore conversation sessions", "green"))
    print(colored("✓ Real-time streaming responses", "green"))
    print()
    print(colored("Try 'Please retrieve details for txnd-3:2007-cv-01697'", "yellow"))
    print(colored("Type 'exit' or 'quit' to end the session", "yellow"))
    print()

    async with agent.run_mcp_servers():
        # Get initial query from user instead of hardcoding
        initial_query = input(colored("What would you like to search for? > ", "cyan"))
        print(colored("Searching...", "yellow"))

        result = await agent.run(initial_query)

        while True:
            print(f"\n{result.output}")
            user_input = input(colored("\n> ", "cyan"))

            # Strip whitespace and convert to lowercase for reliable command checking
            clean_input = user_input.lower().strip()

            if clean_input in ["exit", "quit"]:
                print(colored("Thank you for using Docket Agent. Goodbye!", "cyan"))
                break

            print(colored("Processing...", "yellow"))
            result = await agent.run(user_input, message_history=result.new_messages())


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(colored("\nThank you for using Docket Agent. Goodbye!", "cyan"))
    except Exception as e:
        print(colored(f"\nAn error occurred: {str(e)}", "red"))
