# main.py - 用户答题端

import streamlit as st
import pandas as pd
import os
import random

# --- 配置路径 ---
image_root = "selected_images"
question_bank_csv = "question_bank.csv"
vote_result_csv = "vote_results.csv"

# --- 初始化状态 ---
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "age_group" not in st.session_state:
    st.session_state.age_group = None
if "agree" not in st.session_state:
    st.session_state.agree = False
if "current_qid" not in st.session_state:
    st.session_state.current_qid = 1

# --- 加载题库 ---
question_df = pd.read_csv(question_bank_csv)
total_questions = len(question_df)

# --- 页面设置 ---
st.set_page_config(layout="wide")

# --- 特殊彩蛋 ---
if st.session_state.user_id == "LZB1205":
    st.image("coloregg.jpg", use_column_width=True)
    st.markdown("""
    <div style='text-align: center; padding: 40px; background-color: rgba(0,0,0,0.6); border-radius: 15px;'>
        <h2 style='color: white;'>WX 永远爱 LZB ❤❤</h2>
        <h3 style='color: white;'>祝 LZB 同学考公上岸 🏆</h3>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 0. 欢迎页 ---
if not st.session_state.agree and not st.session_state.user_id:
    st.title("老年人步行环境感知问卷系统")
    st.markdown("""
    ### 📜 欢迎参与本调查问卷
    本问卷旨在收集不同人群对城市街景的感知判断，用于构建“老年友好型步行环境地图”。
    - 共 75 题，每题展示 4 张街景图像
    - 选择您认为最适合老年人步行的一张
    - 所有信息仅用于研究用途
    """)
    if st.button("我已阅读并同意，开始答题"):
        st.session_state.agree = True
        st.rerun()

# --- 1. 用户登录 ---
if st.session_state.agree and not st.session_state.user_id:
    user_id = st.text_input("请输入您的昵称（如 张叔、李阿姨、专家王教授）")
    if st.button("进入问卷"):
        if os.path.exists(vote_result_csv):
            df_existing = pd.read_csv(vote_result_csv)
            if user_id.strip() != "ss" and user_id.strip() in df_existing.get("user_id", []).values:
                st.error("❌ 用户名已被占用，请更换一个昵称。")
                st.stop()
        if user_id.strip() == "":
            st.warning("请输入有效昵称。")
        else:
            st.session_state.user_id = user_id.strip()
            st.rerun()

# --- 2. 选择身份 ---
if st.session_state.user_id and not st.session_state.user_type:
    st.subheader("请选择您的身份：")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("我是专家"):
            st.session_state.user_type = "expert"
            st.rerun()
    with col2:
        if st.button("我是老年人"):
            st.session_state.user_type = "elder"
            st.rerun()

# --- 3. 老年人选择年龄段 ---
if st.session_state.user_type == "elder" and not st.session_state.age_group:
    st.subheader("请选择您的年龄阶段：")
    st.session_state.age_group = st.radio("年龄段：", ["60-64", "65-69", "70-74", "75-79", "80+"])
    st.rerun()

# --- 4. 答题主流程 ---
if st.session_state.user_type and (st.session_state.user_type != "elder" or st.session_state.age_group):
    st.title("老年人步行环境感知问卷系统")
    st.markdown("---")
    st.header("请开始答题：")

    with st.sidebar:
        st.subheader("📋 答题进度")
        for qid in question_df["question_id"]:
            label = f"题 {qid}"
            color = "green" if qid in st.session_state.responses else "gray"
            btn_label = f"🟢 {label}" if color == "green" else f"⚪ {label}"
            if st.button(btn_label, key=f"jump_{qid}"):
                st.session_state.current_qid = qid
                st.rerun()

    if len(st.session_state.responses) == total_questions:
        st.success("🎉 恭喜您已完成所有问卷！感谢参与。")
        st.balloons()
    else:
        qid = st.session_state.current_qid
        current_row = question_df[question_df["question_id"] == qid].iloc[0]
        st.subheader(f"题目 {qid}")
        st.markdown("请选择以下哪张图像最适合老年人步行环境：")
        col = st.columns(4)
        options = [current_row["image_A"], current_row["image_B"], current_row["image_C"], current_row["image_D"]]

        for i in range(4):
            with col[i]:
                img_path = os.path.join(image_root, options[i])
                st.image(img_path, caption=chr(65 + i))
                if st.button(f"选择 {chr(65 + i)}", key=f"btn_{qid}_{i}"):
                    st.session_state.responses[qid] = {
                        "user_id": st.session_state.user_id,
                        "question_id": qid,
                        "image_A": current_row["image_A"],
                        "image_B": current_row["image_B"],
                        "image_C": current_row["image_C"],
                        "image_D": current_row["image_D"],
                        "selected": chr(65 + i),
                        "user_type": st.session_state.user_type,
                        "age_group": st.session_state.age_group if st.session_state.user_type == "elder" else "N/A"
                    }
                    st.session_state.current_qid += 1
                    st.rerun()

    if st.session_state.responses:
        df = pd.DataFrame.from_dict(st.session_state.responses, orient="index")
        if os.path.exists(vote_result_csv):
            df_existing = pd.read_csv(vote_result_csv)
            df_combined = pd.concat([df_existing, df]).drop_duplicates(subset=["user_id", "question_id"], keep="last")
        else:
            df_combined = df
        df_combined.to_csv(vote_result_csv, index=False)