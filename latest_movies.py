from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.tools import tmdb

SYSTEM_PROMPT = """
You are a movie search agent specializing in searching data for current trending movies.
Response with the actual information you find in the tools, don't add any extra formatting or opinions.
The format responses to the user must be in JSON without the triple backtick (```) at the beginning or end.
Return an empty array if you cannot find the information the user is asking.
Do not make up any information.
"""

tools = [tmdb.get_current_trending_movies]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "{query}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)


@tool("latest_trending_movies")
def run_agent_as_tool(query: str) -> str:
    """Retrieves information about the latest trending movies based on user queries.

    It can answer questions related to:
    - Current trending movies
    - Latest movie releases
    - Current popular movies

    Args:
        query: The user query to ask the agent.

    Returns:
        str: The response from the agent. It should be a JSON string.
    """
    run_name = "tmdb-agent"
    print(f"{run_name=} CALLING AGENT AS TOOL {query=}")
    response = agent_executor.with_config({"run_name": run_name}).invoke(
        {"query": query}
    )
    return response["output"]


if __name__ == "__main__":
    response = run_agent_as_tool.run("What is a good movie for today?")
    print(response)
