from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient()

@tool
def web_search(query: str) -> str:
    """Search the web for information"""
    results = tavily_client.search(query)
    return results

agent = create_agent(
    model='gpt-5-mini',
    tools=[web_search],
    checkpointer=InMemorySaver(),
)

async def get_agent_response(prompt: str, thread_id: str) -> dict:
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=prompt)]},
        {"configurable": {"thread_id": thread_id}}
    )
    # Extract the message content from the agent response
    message_content = ""
    if "messages" in result and len(result["messages"]) > 0:
        message_content = result["messages"][-1].content
    else:
        message_content = str(result)
    
    return {"message": message_content}

async def optimize_prompt(prompt: str) -> str:
    system_message = """
    You are an expert prompt optimizer. Improve the following prompt to be more clear and effective for an AI language model.
    Expand scope—what did they mean but not say? Include all relevant details.
    Expand the context—what background information do they need to know? Include all relevant details.
    Expand the task—what is the specific task they want the AI to perform? Include all relevant details.
    Expand the output—what is the specific output they want the AI to produce? Include all relevant details.
    Expand the format—what is the specific format they want the AI to produce? Include all relevant details.
    Expand the language—what is the specific language they want the AI to produce? Include all relevant details.
    Expand the tone—what is the specific tone they want the AI to produce? Include all relevant details.
    Expand the style—what is the specific style they want the AI to produce? Include all relevant details.
    """
    result = await agent.ainvoke(
        {"messages": [
            SystemMessage(content=system_message),
            HumanMessage(content=prompt)
        ]},
        {"configurable": {"thread_id": thread_id}}
    )
    return result["messages"][-1].content