from langchain_core.messages import HumanMessage

from src.graph.nodes.agent import agent

result = agent({"messages": [HumanMessage("지금 몇 시야?")]})
msg = result["messages"][0]
print(msg.tool_calls)  # [{'name': 'get_current_time', ...}] 나오면 성공
print(msg.content)  # 도구 호출일 땐 보통 빈 문자열

result2 = agent({"messages": [HumanMessage("안녕!")]})
msg2 = result2["messages"][0]
print(msg2.tool_calls)  # [] — 도구 불필요 판단
print(msg2.content)  # 일반 인사 답변
