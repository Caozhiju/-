from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType, ChunkConfig, FetchClient

@tool
def import_pdf_paper_from_url(pdf_url: str, paper_title: str = "PDF论文") -> str:
    """
    从URL导入PDF论文到知识库，用于风格学习。

    Args:
        pdf_url: PDF文件的URL
        paper_title: 论文标题（可选）

    Returns:
        导入结果说明
    """
    ctx = request_context.get() or new_context(method="import_pdf_paper_from_url")

    try:
        # 1. 使用FetchClient读取PDF内容
        fetch_client = FetchClient(ctx=ctx)
        response = fetch_client.fetch(url=pdf_url)

        if response.status_code != 0:
            return f"❌ 读取PDF失败：{response.status_message}"

        # 2. 提取文本内容
        text_content = "\n".join(
            item.text for item in response.content if item.type == "text"
        )

        if not text_content.strip():
            return "❌ PDF中没有提取到文本内容"

        # 3. 导入到知识库
        config = Config()
        knowledge_client = KnowledgeClient(config=config, ctx=ctx)

        document = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=text_content,
            metadata={"title": paper_title, "type": "user_paper", "source": "pdf"}
        )

        chunk_config = ChunkConfig(
            separator="\n\n",
            max_tokens=1500,
            remove_extra_spaces=True
        )

        insert_response = knowledge_client.add_documents(
            documents=[document],
            table_name="user_paper_knowledge",
            chunk_config=chunk_config
        )

        if insert_response.code == 0:
            return f"""✅ PDF论文导入成功！

📄 **标题**：{paper_title}
📊 **文档ID**：{insert_response.doc_ids[0] if insert_response.doc_ids else 'N/A'}
📝 **提取文本长度**：{len(text_content)} 字符
📦 **分块数量**：{len(insert_response.doc_ids) if insert_response.doc_ids else 'N/A'}

已添加到知识库，系统将学习这篇论文的写作风格。"""
        else:
            return f"❌ 导入失败：{insert_response.msg}"

    except Exception as e:
        return f"❌ 导入过程中出现错误：{str(e)}"
