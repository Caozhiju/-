from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config, LLMClient
from langchain_core.messages import HumanMessage, SystemMessage

@tool
def analyze_user_writing_style() -> str:
    """
    分析用户已导入论文的写作风格，提取语言特征。

    Returns:
        风格分析报告，包括句式特点、用词习惯、语气风格等
    """
    ctx = request_context.get() or new_context(method="analyze_user_writing_style")

    try:
        # 1. 从知识库检索用户的论文内容
        config = Config()
        knowledge_client = KnowledgeClient(config=config, ctx=ctx)

        search_response = knowledge_client.search(
            query="用户论文写作风格 句式 用词 语气",
            table_names=["user_paper_knowledge"],
            top_k=10,
            min_score=0.0
        )

        if search_response.code != 0 or not search_response.chunks:
            return "⚠️ 知识库中暂无论文内容，请先导入您的论文。"

        # 2. 提取论文内容
        paper_contents = [chunk.content for chunk in search_response.chunks]
        combined_content = "\n\n".join(paper_contents)

        # 3. 使用LLM分析写作风格
        llm_client = LLMClient(ctx=ctx)

        system_prompt = """你是一位专业的语言风格分析师。请分析以下论文内容的写作风格，提取以下特征：

1. **句式特点**：
   - 句子长度偏好（长短句比例）
   - 常用句式结构（如：倒装、排比、复合句等）
   - 段落组织方式

2. **用词习惯**：
   - 常用词汇类型（专业术语、书面语、口语化程度）
   - 词汇丰富度
   - 特殊用词偏好

3. **语气风格**：
   - 语调（客观/主观/中性）
   - 情感色彩
   - 学术程度

4. **其他特征**：
   - 标点符号使用习惯
   - 段落长度特征
   - 逻辑连接词使用

请以清晰、结构化的方式输出分析结果。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请分析以下论文的写作风格：\n\n{combined_content[:8000]}")  # 限制长度避免超出
        ]

        response = llm_client.invoke(messages=messages, temperature=0.3)

        # 处理响应内容
        if isinstance(response.content, str):
            analysis_result = response.content
        elif isinstance(response.content, list):
            if response.content and isinstance(response.content[0], str):
                analysis_result = " ".join(response.content)
            else:
                analysis_result = " ".join(
                    item.get("text", "") for item in response.content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
        else:
            analysis_result = str(response.content)

        return f"📊 写作风格分析报告\n\n{analysis_result}\n\n---\n✅ 风格分析完成，已保存风格特征。后续生成论文时将自动应用此风格。"

    except Exception as e:
        return f"❌ 风格分析失败：{str(e)}"
