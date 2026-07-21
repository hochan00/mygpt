from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.graph.nodes.agent import agent, route_agent_result, tools
from src.graph.state import AgentState

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    route_agent_result,
    {"continue": "tools", "end": END},
)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile(checkpointer=MemorySaver())
