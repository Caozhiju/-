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
    安全地生成论文，支持万字以上长文生成。

    Args:
        topic: 论文主题
        section: 生成部分（full: 全文万字长文, abstract: 摘要, introduction: 引言, body: 正文, conclusion: 结论）

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
            "full": f"""生成一篇完整的万字学术论文，包含以下完整结构：
1. 摘要（200-300字）：概括研究背景、方法、主要发现和结论
2. 关键词（3-5个）
3. 引言（1000-1500字）：研究背景、研究意义、研究现状、研究目标、研究方法
4. 正文（6000-7000字）：包含3-5个小节，每节深入论述一个方面，包括：
   - 理论基础
   - 研究设计/调查方法
   - 数据分析/案例研究
   - 问题分析
   - 对策建议
5. 结论（800-1000字）：总结研究发现，提出建议，指出研究局限和展望
6. 参考文献（5-10条，示例格式）

总字数要求：10000-12000字。""",
            "abstract": f"""生成论文摘要（200-300字），概括研究背景、方法、主要发现和结论。""",
            "introduction": f"""生成论文引言部分（1000-1500字），包括：
- 研究背景与问题提出
- 研究意义与价值
- 文献综述与研究现状
- 研究目标与内容
- 研究方法与路径""",
            "body": f"""生成论文正文部分（6000-7000字），包含3-5个小节：
- 第一节：理论基础或研究框架
- 第二节：研究设计或调查方法
- 第三节：数据分析或案例研究
- 第四节：问题分析
- 第五节：对策建议或优化方案

每个小节1500-2000字，深入论述。""",
            "conclusion": f"""生成论文结论部分（800-1000字），包括：
- 研究发现总结
- 主要结论
- 对策建议或实践意义
- 研究局限
- 未来研究展望"""
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
- 逻辑严密，论证充分
- 数据详实，案例丰富

## 风格示例（学习这些表达方式）
{style_examples[:2000]}

## 重要提示
1. 不要直接复制示例内容，而是学习其表达方式
2. 避免使用可能引起误解的词汇
3. 确保内容积极健康，符合学术伦理
4. 使用标准的学术表达
5. 论文结构完整，逻辑清晰
6. 内容充实，达到字数要求"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请生成关于'{topic}'的论文{section}部分，确保内容充实、结构完整、逻辑清晰。")
        ]

        # 4. 调用LLM生成（大幅增加输出token限制，支持万字长文）
        llm_client = LLMClient(ctx=ctx)
        
        # 根据section设置不同的token限制
        if section == "full":
            max_tokens = 32768  # 完整论文，最多32768 tokens（约20000+字）
        elif section == "body":
            max_tokens = 24576  # 正文部分，最多24576 tokens
        else:
            max_tokens = 16384  # 其他部分，最多16384 tokens

        response = llm_client.invoke(
            messages=messages,
            temperature=0.7,
            max_completion_tokens=max_tokens
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

        # 检查内容长度
        section_requirements = {
            "full": 8000,      # 完整论文至少8000字
            "abstract": 150,    # 摘要至少150字
            "introduction": 800,  # 引言至少800字
            "body": 4000,      # 正文至少4000字
            "conclusion": 600   # 结论至少600字
        }
        
        min_length = section_requirements.get(section, 500)
        if len(cleaned_content) < min_length:
            return f"""⚠️ 生成内容过短（当前{len(cleaned_content)}字，要求至少{min_length}字）

这可能是因为：
1. 遇到了内容安全限制
2. 生成过程中被截断
3. 论文主题需要更多上下文

**建议解决方案**：
1. 尝试生成单个章节
2. 调整论文主题，提供更多背景信息
3. 分多次生成不同章节
4. 检查知识库中的论文是否包含足够的风格示例

当前生成内容：
---
{cleaned_content}
---"""

        # 7. 返回结果
        section_names = {
            "full": "完整论文（万字长文）",
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
📏 **字数要求**：{section_requirements.get(section, 0)}+ 字符

---

{cleaned_content}

---

💡 **提示**：
- 当前已支持万字长文生成（max_completion_tokens: 32768）
- 生成后请进行人工审核和修改
- 如需要更详细的内容，可以分章节生成然后整合
- 建议多次生成不同版本，选择最优版本"""

    except Exception as e:
        error_msg = str(e)

        # 检测是否是内容安全错误
        if "DataInspectionFailed" in error_msg or "inappropriate content" in error_msg:
            return f"""⚠️ 内容安全检查被触发

很抱歉，生成的内容触发了内容安全检查。这可能是因为：

1. 生成过程中某些词汇或表述被误判
2. 论文主题涉及敏感领域
3. 风格模仿时生成了不当内容
4. 生成长文本时某部分触发了过滤规则

**建议解决方案**：
1. 尝试分章节生成，每部分控制在2000字左右
2. 调整论文主题，避免敏感表述
3. 检查知识库中的论文是否包含敏感内容
4. 尝试生成摘要或引言等较短的部分

你可以重新选择一个更合适的主题或生成不同的章节。"""

        # 检测是否是超时错误
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            return f"""⚠️ 生成超时

生成万字长文需要较长时间，当前请求已超时（1200秒）。

**建议解决方案**：
1. 分章节生成：摘要 → 引言 → 正文 → 结论
2. 每次生成一个部分，避免一次性生成过长内容
3. 正文部分可以再细分小节生成

这样可以避免超时问题，同时保证生成质量。"""

        return f"❌ 生成失败：{str(e)}"
