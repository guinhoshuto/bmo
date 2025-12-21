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