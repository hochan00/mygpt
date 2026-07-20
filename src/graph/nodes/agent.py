from src.core.llm import get_llm
from src.graph.state import AgentState
from src.tools.get_current_time import get_current_time

tools = [get_current_time]


def agent(state: AgentState) -> dict:
    llm_with_tools = get_llm().bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
