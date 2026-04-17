from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType, ChunkConfig

@tool
def import_user_paper(paper_content: str, paper_title: str = "未命名论文") -> str:
    """
    将用户撰写的论文导入知识库，用于后续的风格学习和论文生成。

    Args:
        paper_content: 论文的完整文本内容
        paper_title: 论文的标题（可选，用于标识）

    Returns:
        导入结果说明
    """
    ctx = request_context.get() or new_context(method="import_user_paper")

    try:
        config = Config()
        client = KnowledgeClient(config=config, ctx=ctx)

        # 创建文档对象，添加标题作为元数据
        document = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=paper_content,
            metadata={"title": paper_title, "type": "user_paper"}
        )

        # 配置分块策略
        chunk_config = ChunkConfig(
            separator="\n\n",  # 按段落分块
            max_tokens=1500,   # 每块最多1500 tokens
            remove_extra_spaces=True  # 去除多余空格
        )

        # 导入到知识库
        response = client.add_documents(
            documents=[document],
            table_name="user_paper_knowledge",  # 专门用于存储用户论文的数据集
            chunk_config=chunk_config
        )

        if response.code == 0:
            return f"✅ 论文导入成功！\n\n标题：{paper_title}\n文档ID：{response.doc_ids[0] if response.doc_ids else 'N/A'}\n\n已添加到知识库，系统将学习您的写作风格。"
        else:
            return f"❌ 论文导入失败：{response.msg}"

    except Exception as e:
        return f"❌ 导入过程中出现错误：{str(e)}"
