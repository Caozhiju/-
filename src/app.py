import os
import sys
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

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


def main():
    # 侧边栏
    with st.sidebar:
        st.title("📚 论文助手")
        st.markdown("---")
        mode = st.selectbox(
            "选择功能",
            ["💬 智能对话", "📝 论文写作", "✨ 论文润色", "🔍 论文审稿", "🎓 风格学习"],
        )
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "上传论文（学习风格）",
            type=["pdf", "txt"],
        )
        
        if uploaded_file:
            if st.button("📤 学习风格", type="primary"):
                with st.spinner("正在分析论文..."):
                    save_path = f"assets/{uploaded_file.name}"
                    os.makedirs("assets", exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    if uploaded_file.type == "application/pdf":
                        prompt = f"请导入PDF文件学习写作风格，文件路径：{save_path}"
                    else:
                        prompt = f"请导入文本文件学习写作风格，文件路径：{save_path}"
                    
                    st.session_state.messages.append(HumanMessage(content=prompt))
                    st.success("✅ 风格学习完成！")

        if st.button("🗑️ 清除对话"):
            st.session_state.messages = []
            st.success("对话已清除！")
            st.rerun()

    st.title("📚 国际中文教育论文助手")
    
    if not init_agent():   如果不是init_agent()：
        st.error("无法初始化智能体，请检查配置。")
        return   返回

    st.info("💬 请选择左侧功能并开始对话")

    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

    user_input = st.chat_input("输入你的问题或需求...", key="chat_input")user_input = st.chat_input("输入你的问题或需求...", key="chat_input")

    if user_input:   如果user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))st.session_state.messages   消息.append   附加 HumanMessage (content = user_input))
        
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("正在思考..."):with   与 st.spinner   微调控制项("正在思考..."):
            try:   试一试:
                config = {"configurable": {"thread_id": st.session_state.thread_id}}Config = {"configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"   "configurable"; {"thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"   "thread_id"; st.session_state.thread_id}}
                response = st.session_state.agent.invoke(Response = st.session_state.agent   代理.invoke   调用(
                    {"messages": st.session_state.messages},{"messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages": st.session_state.messages   消息},
                    config=config   problem = problem
                )

                if response and "messages" in response:如果response和"；messages"   配置；在response中：
                    ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage)]ai_messages = [m for m in   在 response["messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"   "messages"] if   如果 isinstance(m, AIMessage)]
                    if ai_messages:   如果ai_messages:
                        ai_response = ai_messages[-1].contentAi_response = ai_messages[-1].content   内容
                        st.session_state.messages.append(AIMessage(content=ai_response))st.session_state.messages   消息.append   附加 AIMessage (content = ai_response))
                        
                        with st.chat_message("assistant"):
                            st.write(ai_response)

            except Exception as e:   例外情况如下：
                error_msg = f"错误: {str(e)}"
                st.session_state.messages.append(AIMessage(content=error_msg))st.session_state.messages   消息.append   附加 (AIMessage(内容= error_msg))
                with st.chat_message("assistant"):
                    st.error(error_msg)

        st.rerun()


if __name__ == "__main__":   如果__name__ == "__main__"；
    main()
