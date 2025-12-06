import streamlit as st
from openai import OpenAI

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="无限世界 RPG", page_icon="🎲")
st.title("🎲 无限世界: AI 互动文字游戏")

# --- 2. 侧边栏：输入 API Key ---
with st.sidebar:
    st.header("🔑 启动钥匙")
    api_key = st.text_input("请输入 OpenAI API Key", type="password", help="你需要一个 API Key 才能连接 AI 大脑")
    st.markdown("---")
    st.markdown("**游戏说明**：\n1. 输入你想玩的背景\n2. AI 会生成开场\n3. 你输入行动，AI 判定结果")
    if st.button("重置游戏"):
        st.session_state.messages = []
        st.session_state.game_started = False
        st.rerun()

# 检查 Key 是否存在
if not api_key:
    st.warning("⚠️ 请在左侧侧边栏输入 API Key 才能开始游戏！")
    st.stop()

# 初始化客户端
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"API Key 格式似乎不对: {e}")
    st.stop()

# --- 3. 游戏状态管理 ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. 游戏开始前的：设定界面 ---
if not st.session_state.game_started:
    st.markdown("### 🛠️ 第一步：创建你的世界")
    col1, col2 = st.columns(2)
    with col1:
        world_setting = st.text_input("世界背景", value="克苏鲁风格的1920年伦敦侦探故事")
    with col2:
        player_role = st.text_input("你的角色", value="一名落魄的私家侦探，随身带着一把左轮")

    start_btn = st.button("开始冒险！", type="primary")

    if start_btn:
        # 核心：这是给 AI 的“催眠指令” (System Prompt)
        system_prompt = f"""
        你现在是一个专业的文字冒险游戏 GM（主持人）。

        【游戏设定】
        世界观：{world_setting}
        玩家角色：{player_role}

        【你的职责】
        1. 描述剧情环境，氛围要沉浸。
        2. 当玩家行动时，逻辑判断其成功率（不要总是让玩家成功，要有挑战）。
        3. 如果遇到战斗或危机，给出“QTE”感觉的紧迫描述。
        4. 每次回复后，不要替玩家做决定，而是停下来等待玩家输入。
        5. 输出格式：请用 Markdown 格式，重要物品加粗，地名用斜体。

        现在，请生成游戏的开场剧情。
        """

        st.session_state.messages.append({"role": "system", "content": system_prompt})

        with st.spinner("AI 正在构建世界..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages
                )
                first_msg = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": first_msg})
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"连接 AI 失败，请检查网络或 API Key。错误信息: {e}")

# --- 5. 游戏进行中的：聊天界面 ---
else:
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("你打算做什么？"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages,
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"AI 掉线了: {e}")
