from dotenv import load_dotenv

load_dotenv()

import os

from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])

result = notion.search()
print(f"접근 가능한 항목: {len(result['results'])}개\n")

for item in result["results"]:
    obj_type = item["object"]  # page or database
    # 제목 뽑기 (페이지마다 구조가 조금씩 달라서 안전하게)
    title = "제목 없음"
    props = item.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title" and prop["title"]:
            title = prop["title"][0]["plain_text"]
            break
    print(f"- [{obj_type}] {title}")
