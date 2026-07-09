from langgraph.graph import END, START, StateGraph

from src.graph.nodes.generation import generate, refuse_answer
from src.graph.nodes.grading import (
    grade_documents,
    grade_hallucination,
    route_documents_result,
    route_hallucination_result,
)
from src.graph.nodes.retrieval import retrieve
from src.graph.state import GraphState

graph_builder = StateGraph(GraphState)

graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_node("grade_hallucination", grade_hallucination)
graph_builder.add_node("refuse_answer", refuse_answer)
graph_builder.add_node("grade_documents", grade_documents)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "grade_documents")
graph_builder.add_edge("generate", "grade_hallucination")
graph_builder.add_edge("refuse_answer", END)

graph_builder.add_conditional_edges(
    "grade_documents",
    route_documents_result,
    {"generate": "generate", "refuse": "refuse_answer", "transform": "transform_query"},
)
graph_builder.add_conditional_edges(
    "grade_hallucination",
    route_hallucination_result,
    {"end": END, "retry": "generate", "refuse": "refuse_answer"},
)

graph = graph_builder.compile()
