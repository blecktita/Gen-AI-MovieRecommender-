"""Example LangChain server exposes a conversational retrieval agent.

Relevant LangChain documentation:

* Creating a custom agent: https://python.langchain.com/docs/modules/agents/how_to/custom_agent
* Streaming with agents: https://python.langchain.com/docs/modules/agents/how_to/streaming#custom-streaming-with-events
* General streaming documentation: https://python.langchain.com/docs/expression_language/streaming

**ATTENTION**
1. To support streaming individual tokens you will need to use the astream events
   endpoint rather than the streaming endpoint.
2. This example does not truncate message history, so it will crash if you
   send too many messages (exceed token length).
3. The playground at the moment does not render agent output well! If you want to
   use the playground you need to customize it's output server side using astream
   events by wrapping it within another runnable.
4. See the client notebook it has an example of how to use stream_events client side!
"""
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.agents import latest_movies, netflix_shows

SYSTEM_PROMPT = """
## Who You are

You are a specialized movie recommendation chatbot.

Your primary function is to provide users with movie and TV show recommendations based on their preferences. Additionally, you can provide factual information about these movies and shows. You are equipped with advanced recommendation tools to assist you in generating accurate responses.

## Your Mission

Your mission is to answer questions related with movie recommendations or movie information finance with the highest level of accuracy. The questions MUST be related to the following:

- Netflix Shows and Movies
- Latest trending movies

## Specific Instructions

- NEVER make up information. Respond only with the information available in the context retrieved by your tools.
- Always evaluate that the context provided is relevant to the user query. If the context doesn't contain relevant information, you should inform the user that you don't have the required data.
- In the event of an error while retrieving information from the recommendation tools, kindly apologize to the user and inform them about the issue.
- Do not respond questions outside or your mission scope.
- In addition to the user preference, use the movie ratings to support your recommendations.
- Avoid giving the user to many recommendations. Limit the number of recommendations to 3-4.
"""

tools = [
    netflix_shows.run_agent_as_tool,
    latest_movies.run_agent_as_tool,
]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        # Please note that the ordering of the user input vs.
        # the agent_scratchpad is important.
        # The agent_scratchpad is a working space for the agent to think,
        # invoke tools, see tools outputs in order to respond to the given
        # user input. It has to come AFTER the user input.
        ("user", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# We need to set streaming=True on the LLM to support streaming individual tokens.
# Tokens will be available when using the stream_log / stream events endpoints,
# but not when using the stream endpoint since the stream implementation for agent
# streams action observation pairs not individual tokens.
# See the client notebook that shows how to use the stream events endpoint.
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    verbose=True,
)

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)


# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.
class Input(BaseModel):
    question: str


class Output(BaseModel):
    output: Any


agent_executor = (
    AgentExecutor(agent=agent, tools=tools)
    .with_types(input_type=Input, output_type=Output)
    .with_config({"run_name": "agent"})
)
