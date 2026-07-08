from langgraph.graph import END, START, StateGraph

from src.graph.nodes.generation import generate
from src.graph.nodes.grading import grade_hallucination, route_after_hallucination_check
from src.graph.nodes.retrieval import retrieve
from src.graph.state import GraphState

graph_builder = StateGraph(GraphState)

graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_node("grade_hallucination", grade_hallucination)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", "grade_hallucination")

graph_builder.add_conditional_edges(
    "grade_hallucination",
    route_after_hallucination_check,
    {"end": END, "retry": "generate"},
)

graph = graph_builder.compile()
