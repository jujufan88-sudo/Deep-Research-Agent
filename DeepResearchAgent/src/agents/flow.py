# src/workflows/simple_flow.py
"""简单版研究流程 — 纯函数串联"""

from src.agents.planner import create_planner, parse_plan
from src.agents.researcher import create_researcher_agent
from src.agents.synthesizer import create_synthesizer


def run_research(topic: str) -> str:
    """执行完整的研究流程"""

    print(f"\n{'='*60}")
    print(f"开始研究: {topic}")
    print(f"{'='*60}")

    # Step 1: 规划
    print("\n[Step 1/3] 拆解研究问题...")
    planner = create_planner()
    raw = planner.invoke({"topic": topic})
    plan = parse_plan(raw.content, topic)

    print(f"  拆解为 {len(plan.sub_questions)} 个子问题:")
    for i, q in enumerate(plan.sub_questions, 1):
        print(f"    {i}. {q}")

    # Step 2: 逐个研究
    print(f"\n[Step 2/3] 逐个研究子问题...")
    researcher = create_researcher_agent()
    all_findings = []

    for i, question in enumerate(plan.sub_questions, 1):
        print(f"\n  研究问题 {i}/{len(plan.sub_questions)}: {question}")
        result = researcher.invoke({"messages": [
            {"role": "user", "content": question}
        ]})
        answer = result["messages"][-1].content
        finding = f"[Finding {i}] Q: {question}\nA: {answer}\n"
        all_findings.append(finding)
        print(f"  问题 {i} 研究完成")

    # Step 3: 综合报告
    print(f"\n[Step 3/3] 生成研究报告...")
    synthesizer = create_synthesizer()
    report = synthesizer.invoke({
        "topic": topic,
        "findings": "\n---\n".join(all_findings)
    })

    print(f"\n{'='*60}")
    print("研究完成！")
    print(f"{'='*60}")

    return report.content


if __name__ == "__main__":
    topic = input("请输入研究内容：")
    report = run_research(topic)

    with open("research_report.md", "w") as f:
        f.write(report)

    print(f"\n报告已保存到 research_report.md")
    print(f"\n报告预览（前500字）:\n")
    print(report[:500])
