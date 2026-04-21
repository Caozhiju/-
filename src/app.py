import   进口   进口的 os
import   进口   导入系统 sys
import   进口   将streamlit导入为st streamlit as   作为 st
from从langchain_core。消息导入HumanMessage， AIMessage   从 langchain_core.messages   消息   消息 import   进口   进口 HumanMessage, AIMessage

# 添加项目根目录到 Python 路径
sys.sys   路径.path。插入(0,os.path   路径.dirname (os.path   路径.dirname (os.path   路径.abspath (__file__))))path.insert   插入(0, os.path   路径.dirname(os.path   路径.dirname(os.path   路径.abspath(__file__))))

from从代理。Agent导入build_agent agents.   从agent import   进口 build_agent

# 页面配置
st.set_page_config(
    page_title="国际中文教育论文助手",
    page_icon=   page_icon="📚","📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚"   "📚",
    layout=   布局=“wide","wide   "wide"",   “,   “,
    initial_sidebar_state=initial_sidebar_state =“expanded""expanded"   "expanded"
)

# 初始化 session state如果messages"；不在st.session_state：   如果
if "messages" not in st.session_state:如果messages"；不在st.session_state：
    st.session_state.messages = []如果"；agent"；不在st.session_state中：   如果

if "agent" not in st.session_state:如果"；agent"；不在st.session_state中：
    st.session_state.agent = None如果thread_id不在st.session_state中：   如果

if "thread_id" not in st.session_state:如果thread_id不在st.session_state中：
    st.session_state.thread_id = "session_001"st.session_state。Thread_id = "session_001"；st.session_state。Thread_id = "session_001"st.session_state。Thread_id = "session_001"；


def init_agent():
    """初始化 Agent"""   """初始化 Agent""""""初始化 Agent"""   """初始化 Agent"""
    if st.session_state.agent is None:   """初始化 Agent"""
        with st.spinner("正在初始化智能体..."):with st.spinner("正在初始化智能体..."):
            try:   试一试:
                st.session_state.agent = build_agent()   试一试:st.session_state。Agent = build_agent（）
                return True   还真
            except Exception as e:   例外情况如下：
                st.error(f"初始化失败: {str(e)}")st.error(f"初始化失败: {str(e)}")
                return False   返回假
    return True   还真


def main():
    # 侧边栏
    with st.sidebar:   st.sidebar:
        st.title("📚 论文助手")   st.title("📚 论文助手")
        st.markdown("---")   st.markdown(“-”)
        mode = st.selectbox(   Mode = st。
            "选择功能",
            ["💬 智能对话", "📝 论文写作", "✨ 论文润色", "🔍 论文审稿", "🎓 风格学习"],
        )
        st.markdown("---")   st.markdown(“-”)
        
        uploaded_file = st.file_uploader(Uploaded_file = st.file_uploader(
            "上传论文（学习风格）",
            type=["pdf", "txt"],   type=["pdf", "txt"],
        )
        
        if uploaded_file:   如果uploaded_file:
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
