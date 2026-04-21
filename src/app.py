import os
import sys
from typing import List, Dict, Any
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import build_agent

# 页面配置
st.set_page_config(
    page_title="国际中文教育论文助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
""", unsafe_allow_html=True)

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "session_001"


def init_agent():
    """初始化 Agent"""
    if st.session_state.agent is None:
        with st.spinner("正在初始化智能体..."):
            try:
                st.session_state.agent = build_agent()
                return True
            except Exception as e:
                st.error(f"初始化失败: {str(e)}")
                return False
    return True


def render_message(role: str, content: str):
    """渲染消息"""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message"><strong>👤 用户:</strong><br>{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 助手:</strong><br>{content}</div>', unsafe_allow_html=True)


def main():
    # 侧边栏
    with st.sidebar:
        st.title("📚 论文助手")
        st.markdown("---")

        # 功能选择
        st.subheader("功能选择")
        mode = st.selectbox(
            "选择功能",
            ["💬 智能对话", "📝 论文写作", "✨ 论文润色", "🔍 论文审稿", "🎓 风格学习"],
            help="选择你想要使用的功能"
        )

        st.markdown("---")

        # 风格学习说明
        st.subheader("🎓 风格学习")
        st.markdown("""
        **如何学习你的风格？**

        1. 上传你的论文（PDF或TXT）
        2. 点击"学习风格"按钮
        3. 系统会分析并记住你的写作风格
        4. 之后的生成会模仿你的风格
        """)

        # 文件上传
        uploaded_file = st.file_uploader(
            "上传论文（学习风格）",
            type=["pdf", "txt"],
            help="上传你已完成的论文，系统会学习你的写作风格"
        )

        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 学习风格", type="primary"):
                    with st.spinner("正在分析论文..."):
                        # 保存上传的文件
                        save_path = f"assets/{uploaded_file.name}"
                        os.makedirs("assets", exist_ok=True)
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # 调用导入工具
                        if uploaded_file.type == "application/pdf":
                            prompt = f"请导入PDF文件学习写作风格，文件路径：{save_path}"
                        else:
                            prompt = f"请导入文本文件学习写作风格，文件路径：{save_path}"

                        # 添加到消息中
                        st.session_state.messages.append(HumanMessage(content=prompt))
                        st.success("✅ 风格学习完成！之后生成的论文会模仿你的写作风格。")

        st.markdown("---")

        # 使用说明
        st.subheader("📖 使用说明")
        st.markdown("""
        **对话功能：**
        - 直接输入问题或需求
        - 支持多轮对话
        - 记住上下文

        **论文写作：**
        - 输入论文主题
        - 指定字数和要求
        - 自动生成论文

        **风格学习：**
        - 上传1-3篇你的论文
        - 系统自动学习风格
        - 生成个性化论文
        """)

        st.markdown("---")

        # 清除对话
        if st.button("🗑️ 清除对话"):
            st.session_state.messages = []
            st.success("对话已清除！")
            st.rerun()

        # 显示统计
        if st.session_state.messages:
            st.markdown("---")
            st.subheader("📊 对话统计")
            st.metric("对话轮次", len([m for m in st.session_state.messages if isinstance(m, HumanMessage)]))

    # 主标题
    st.title("📚 国际中文教育论文助手")
    st.markdown("智能写作 • 风格学习 • 专业审稿")

    st.markdown("---")

    # 初始化 Agent
    if not init_agent():
        st.error("无法初始化智能体，请检查配置。")
        return

    # 显示当前功能模式
    mode_messages = {
        "💬 智能对话": "🤖 我可以帮你解答任何问题，支持多轮对话。",
        "📝 论文写作": "✍️ 输入主题和要求，我会帮你生成专业的国际中文教育论文。",
        "✨ 论文润色": "✨ 发送你的论文草稿，我会优化表达和学术规范性。",
        "🔍 论文审稿": "🔍 发送你的论文，我会检查内容和结构问题。",
        "🎓 风格学习": "🎓 在侧边栏上传你的论文，我会学习你的写作风格。"
    }

    st.info(mode_messages[mode])

    # 显示历史消息
    message_container = st.container()
    with message_container:
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                render_message("user", msg.content)
            elif isinstance(msg, AIMessage):
                render_message("assistant", msg.content)

    # 用户输入
    user_input = st.chat_input("输入你的问题或需求...", key="chat_input")

    if user_input:
        # 根据选择的功能添加提示
        if mode == "📝 论文写作":
            user_input = f"请帮我写一篇国际中文教育论文，主题和要求如下：\n\n{user_input}"
        elif mode == "✨ 论文润色":
            user_input = f"请润色以下论文草稿，优化表达和学术规范性：\n\n{user_input}"
        elif mode == "🔍 论文审稿":
            user_input = f"请审稿以下论文，检查内容和结构问题：\n\n{user_input}"

        # 添加用户消息
        st.session_state.messages.append(HumanMessage(content=user_input))

        # 显示用户消息
        render_message("user", user_input)

        # 生成回复
        with st.spinner("正在思考..."):
            try:
                # 调用 Agent
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                response = st.session_state.agent.invoke(
                    {"messages": st.session_state.messages},
                    config=config
                )

                # 提取最后一条 AI 消息
                if response and "messages" in response:
                    ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage)]
                    if ai_messages:
                        ai_response = ai_messages[-1].content
                        st.session_state.messages.append(AIMessage(content=ai_response))

                        # 显示 AI 消息
                        render_message("assistant", ai_response)

            except Exception as e:
                error_msg = f"生成回复时出错: {str(e)}"
                st.session_state.messages.append(AIMessage(content=error_msg))
                render_message("assistant", error_msg)
                st.error(error_msg)

        # 滚动到底部
        st.rerun()


if __name__ == "__main__":
    main()
