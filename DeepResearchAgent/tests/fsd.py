#
# from langchain_openai import ChatOpenAI
#
# llm = ChatOpenAI(
#     model="mimo-v2.5",  # SMART_MODEL 的值
#     api_key="tp-c6i5hq5s8ei2ymk88soee6t6zyhapnxfrf16gc9skg0nqg0j",
#     base_url="https://token-plan-cn.xiaomimimo.com/v1",
# )
#
# # 简单调用，不走 Agent，只测 LLM 能不能通
# response = llm.invoke("你好，请用一句话介绍你自己")
# print(response.content)

# import requests
#
# response = requests.get(
#     "https://token-plan-cn.xiaomimimo.com/v1/models",
#     headers={"Authorization": "Bearer tp-c6i5hq5s8ei2ymk88soee6t6zyhapnxfrf16gc9skg0nqg0j"},
# )
# print(response.json())

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("MIMO_API_KEY")
print(f"[DEBUG] MIMO_API_KEY: {api_key[:10]}..." if api_key else "[ERROR] MIMO_API_KEY is None!")