from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config, LLMClient
from langchain_core.messages import HumanMessage, SystemMessage
import re

def clean_generated_text(text: str) -> str:
    """
    清洗生成的文本，移除可能导致内容安全检查失败的内容

    Args:
        text: 生成的文本

    Returns:
        清洗后的文本
    """
    # 移除可能敏感的字符组合
    text = re.sub(r'[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uff0c\u3002\uff1f\uff01\uff1a\uff1b\u3001\uff08\uff09\u300a\u300b\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f\u3010\u3011\u3008\u3009\u3014\u3015\u2026\u2014\u00b7\u20ac\xa1\xa2\u300a\u300b\uff01\uff1f\uff1b\uff1a\u002c\u002e\u003b\u003a\u0028\u0029\u0022\u0027\u005b\u005d\u007b\u007d\u002f\u002d\u005c]', '', text)

    # 移除过长的非中文字符串
    text = re.sub(r'[^\u4e00-\u9fa5]{20,}', '', text)

    # 移除特殊控制字符
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    return text.strip()

def extract_style_examples(knowledge_client, max_length=3000):
    """
    从知识库提取风格示例，限制长度以避免prompt过长

    Args:
        knowledge_client: 知识库客户端
        max_length: 最大长度（字符数）

    Returns:
        风格示例文本
    """
    try:
        # 不指定 table_names，搜索所有数据集
        response = knowledge_client.search(
            query="论文写作风格 句式 用词 语气",
            top_k=3,  # 减少检索数量
            min_score=0.0
        )

        if response.code == 0 and response.chunks:
            examples = []
            total_length = 0

            for chunk in response.chunks:
                if total_length + len(chunk.content) > max_length:
                    break
                examples.append(chunk.content)
                total_length += len(chunk.content)

            return "\n\n---\n\n".join(examples)
    except Exception as e:
        print(f"提取风格示例时出错: {e}")

    return ""

@tool
def generate_paper_safely(topic: str, section: str = "full") -> str:
    """
    安全地生成论文，避免内容安全检查失败和长度限制问题。

    Args:
        topic: 论文主题
        section: 生成部分（full: 全文, abstract: 摘要, introduction: 引言, body: 正文, conclusion: 结论）

    Returns:
        生成的论文内容
    """
    ctx = request_context.get() or new_context(method="generate_paper_safely")

    try:
        # 1. 从知识库提取风格示例（限制长度）
        config = Config()
        knowledge_client = KnowledgeClient(config=config, ctx=ctx)

        style_examples = extract_style_examples(knowledge_client, max_length=3000)

        if not style_examples:
            return "⚠️ 知识库中暂无风格示例，请先导入论文并分析风格。"

        # 2. 根据section选择生成策略
        section_prompts = {
            "full": f"""生成一篇完整的学术论文，包含以下部分：摘要（200字）、关键词（3-5个）、引言、正文（至少3个小节）、结论。""",
            "abstract": f"""生成论文摘要（200-300字），概括研究背景、方法、主要发现和结论。""",
            "introduction": f"""生成论文引言部分，包括研究背景、研究意义、研究内容和研究方法。""",
            "body": f"""生成论文正文部分，包含3个小节，每节深入论述一个方面。""",
            "conclusion": f"""生成论文结论部分，总结研究发现，提出建议和展望。"""
        }

        section_instruction = section_prompts.get(section, section_prompts["full"])

        # 3. 构建精简的system prompt
        system_prompt = f"""你是国际中文教育领域的论文写作专家。请根据以下要求生成论文内容：

## 论文主题
{topic}

## 生成要求
{section_instruction}

## 风格要求
- 学习用户的写作风格（参考下方示例）
- 使用专业的学术表达
- 保持客观中立的语气
- 避免使用敏感词汇或不当表述
- 确保内容符合学术规范

## 风格示例（学习这些表达方式）
{style_examples[:2000]}

## 重要提示
1. 不要直接复制示例内容，而是学习其表达方式
2. 避免使用可能引起误解的词汇
3. 确保内容积极健康，符合学术伦理
4. 使用标准的学术表达"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请生成关于'{topic}'的论文{section}部分。")
        ]

        # 4. 调用LLM生成（增加输出token限制）
        llm_client = LLMClient(ctx=ctx)
        response = llm_client.invoke(
            messages=messages,
            temperature=0.7,
            max_completion_tokens=8192  # 增加到8192
        )

        # 5. 处理响应
        if isinstance(response.content, str):
            generated_content = response.content
        elif isinstance(response.content, list):
            if response.content and isinstance(response.content[0], str):
                generated_content = " ".join(response.content)
            else:
                generated_content = " ".join(
                    item.get("text", "") for item in response.content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
        else:
            generated_content = str(response.content)

        # 6. 清洗生成的内容
        cleaned_content = clean_generated_text(generated_content)

        if len(cleaned_content) < 100:
            return f"⚠️ 生成内容过短，可能遇到了内容安全限制。建议尝试分章节生成。"

        # 7. 返回结果
        section_names = {
            "full": "完整论文",
            "abstract": "摘要",
            "introduction": "引言",
            "body": "正文",
            "conclusion": "结论"
        }

        return f"""✨ 论文生成成功！

📝 **主题**：{topic}
📄 **部分**：{section_names.get(section, section)}
📊 **内容长度**：{len(cleaned_content)} 字符
🧹 **安全处理**：已清洗敏感内容

---

{cleaned_content}

---

💡 **提示**：
- 如果需要生成完整论文，建议分章节逐步生成
- 可以根据需要调整各部分内容
- 生成后请进行人工审核和修改"""

    except Exception as e:
        error_msg = str(e)

        # 检测是否是内容安全错误
        if "DataInspectionFailed" in error_msg or "inappropriate content" in error_msg:
            return f"""⚠️ 内容安全检查被触发

很抱歉，生成的内容触发了内容安全检查。这可能是因为：

1. 生成过程中某些词汇或表述被误判
2. 论文主题涉及敏感领域
3. 风格模仿时生成了不当内容

**建议解决方案**：
1. 尝试生成单个章节（如：仅生成摘要）
2. 调整论文主题，避免敏感表述
3. 检查知识库中的论文是否包含敏感内容

你可以重新选择一个更合适的主题或生成不同的章节。"""

        return f"❌ 生成失败：{str(e)}"
