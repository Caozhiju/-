from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config, LLMClient
from langchain_core.messages import HumanMessage, SystemMessage

@tool
def generate_personalized_paper(topic: str, paper_type: str = "研究论文") -> str:
    """
    基于用户已导入论文的写作风格，生成指定主题的新论文。

    Args:
        topic: 论文主题或标题
        paper_type: 论文类型（如：研究论文、综述论文、教学反思等）

    Returns:
        生成的新论文内容
    """
    ctx = request_context.get() or new_context(method="generate_personalized_paper")

    try:
        # 1. 从知识库检索用户的论文示例
        config = Config()
        knowledge_client = KnowledgeClient(config=config, ctx=ctx)

        search_response = knowledge_client.search(
            query="论文写作风格 示例 文章内容",
            table_names=["user_paper_knowledge"],
            top_k=5,
            min_score=0.0
        )

        if search_response.code != 0 or not search_response.chunks:
            return "⚠️ 知识库中暂无论文示例，请先导入您的论文并分析风格。"

        # 2. 提取论文示例
        paper_examples = [chunk.content for chunk in search_response.chunks]
        examples_text = "\n\n---\n\n".join(paper_examples)

        # 3. 使用LLM生成个性化论文
        llm_client = LLMClient(ctx=ctx)

        system_prompt = f"""你是一位国际中文教育领域的论文写作专家。请根据以下要求生成一篇{paper_type}。

## 重要要求

1. **严格模仿用户的写作风格**：
   - 参考下方提供的用户论文示例
   - 学习用户的句式结构、用词习惯、语气风格
   - 保持与用户论文相似的学术程度和表达方式

2. **论文主题**：{topic}

3. **论文结构**：
   - 摘要（200-300字）
   - 关键词（3-5个）
   - 引言/绪论
   - 正文（根据论文类型展开）
   - 结论
   - 参考文献（示例格式）

4. **国际中文教育领域**：
   - 确保内容符合国际中文教育专业规范
   - 使用准确的学科术语
   - 理论与实践结合

5. **风格一致性**：
   - 不要使用通用的模板化表达
   - 每一句都应体现用户的写作特色
   - 保持学术性但要有个人风格

## 用户论文示例（请严格学习其风格）：

{examples_text[:10000]}

请开始生成论文："""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请基于上述风格生成关于'{topic}'的{paper_type}。")
        ]

        response = llm_client.invoke(messages=messages, temperature=0.7)

        # 处理响应内容
        if isinstance(response.content, str):
            generated_paper = response.content
        elif isinstance(response.content, list):
            if response.content and isinstance(response.content[0], str):
                generated_paper = " ".join(response.content)
            else:
                generated_paper = " ".join(
                    item.get("text", "") for item in response.content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
        else:
            generated_paper = str(response.content)

        return f"✨ 个性化论文生成成功！\n\n**主题**：{topic}\n**类型**：{paper_type}\n\n---\n\n{generated_paper}\n\n---\n💡 提示：这篇论文模仿了您的写作风格，您可以根据需要进行调整。"

    except Exception as e:
        return f"❌ 论文生成失败：{str(e)}"
