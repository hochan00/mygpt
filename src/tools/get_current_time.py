from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """현재 날짜와 시각을 반환한다. 사용자가 지금 몇 시인지, 오늘이 며칠인지 물어볼 때 사용한다."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
