
import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

import os

async def run_memory_chat():
    """Run a chat using MCP agent built-in conversation memory."""
    # Load environment variable for api keys
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # Config file path - change this to your config file
    config_file = "server/weather.json"

    print("Loading config...")

    # create MCP client and agent with memory enabled
    client = MCPClient.from_config_file(config_file)
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with memory_enabled=true
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,  # Enable built-in conversation memory
    )

    print("Starting chat...")
    print("Type 'exit' or 'quit' to exit.")
    print("Type 'help' or '?' for more information.")

    try:
        # Main chat loop
        while True:
            # Get user  input
            user_input = input("\nYour input: ")

            # Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            elif user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Clearing conversation history...")
                continue

            # get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_memory_chat())