# frontend/app.py
"""Streamlit 前端 — 研究助手交互界面"""

import streamlit as st
import requests
import time

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔍",
    layout="wide",
)

# 自定义样式
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
    }
    .research-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    h1 { color: #58a6ff !important; }
    h2 { color: #79c0ff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Deep Research Agent")
st.markdown("输入一个研究主题，AI 将自动规划、搜索、验证并生成研究报告。")

# 侧边栏 — 历史搜索
with st.sidebar:
    st.header("📚 历史研究")
    memory_query = st.text_input("搜索历史研究...")
    if memory_query:
        resp = requests.get(f"{API_BASE}/search-memory", params={"query": memory_query})
        if resp.status_code == 200:
            for r in resp.json()["results"]:
                with st.expander(r["content"][:80] + "..."):
                    st.write(r["content"])
                    st.caption(f"相关度: {1 - r['relevance_score']:.2f}")

# 主区域
topic = st.text_input(
    "研究主题",
    placeholder="e.g., How are companies using AI agents in production?",
)

col1, col2 = st.columns([1, 4])
with col1:
    max_q = st.slider("子问题数量", 3, 7, 5)
with col2:
    save_memory = st.checkbox("保存到记忆", value=True)

if st.button("🚀 开始研究", type="primary", disabled=not topic):

    # 进度显示
    progress_bar = st.progress(0)
    status = st.empty()

    status.text("📋 正在规划研究方案...")
    progress_bar.progress(10)

    with st.spinner("正在执行深度研究，请稍候..."):
        try:
            response = requests.post(
                f"{API_BASE}/research",
                json={
                    "topic": topic,
                    "max_sub_questions": max_q,
                    "save_to_memory": save_memory,
                },
                timeout=300000,
            )

            if response.status_code == 200:
                result = response.json()
                progress_bar.progress(100)
                status.text("✅ 研究完成！")

                # 显示子问题
                st.subheader("📋 研究计划")
                for i, q in enumerate(result["sub_questions"], 1):
                    st.write(f"**{i}.** {q}")

                # 显示报告
                st.subheader("📊 研究报告")
                st.markdown(result["report"])

                # 统计信息
                st.caption(f"来源数量: {result['num_sources']} | 研究主题: {result['topic']}")

            else:
                st.error(f"研究失败: {response.text}")

        except requests.exceptions.Timeout:
            st.error("研究超时，请缩短研究主题范围后重试。")
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
