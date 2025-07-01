import pandas as pd
import os
import random
import streamlit as st
import trueskill
import zipfile
with zipfile.ZipFile('selected_images.zip', 'r') as zip_ref:
    zip_ref.extractall('selected_images')

# --- 参数配置 ---
csv_path = r"D:\Desktop\wx-2article\code\community_cluster_result.csv"     # 聚类结果CSV文件
image_root = r"D:\Desktop\wx-2article\selected_images"                          # 图像根目录
question_bank_csv = r"D:\Desktop\wx-2article\code\question_bank.csv"        # 题库文件
vote_result_csv = "vote_results.csv"           # 投票记录文件

# --- 加载题库 ---
question_df = pd.read_csv(question_bank_csv)
total_questions = len(question_df)

# --- 初始化会话状态 ---
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "age_group" not in st.session_state:
    st.session_state.age_group = None

# --- 设置网页结构 ---
st.set_page_config(layout="wide")
st.title("老年人步行性问卷评分系统")

# --- 用户身份选择 ---
if st.session_state.user_type is None:
    st.subheader("请选择您的身份：")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("我是专家"):
            st.session_state.user_type = "expert"
    with col2:
        if st.button("我是老年人"):
            st.session_state.user_type = "elder"

# --- 年龄段选择（仅限老年人） ---
if st.session_state.user_type == "elder" and st.session_state.age_group is None:
    st.subheader("请选择您的年龄阶段：")
    st.session_state.age_group = st.radio("年龄段：", ["60-64", "65-69", "70-74", "75-79", "80+"])

# --- 进入答题界面 ---
if st.session_state.user_type:
    st.markdown("---")
    st.header("请开始答题：")

    # 左侧展示进度和导航
    with st.sidebar:
        st.subheader("答题进度：")
        for qid in question_df["question_id"]:
            if qid in st.session_state.responses:
                st.markdown(f"<span style='color:green'>✔ 题目 {qid}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:gray'>❌ 题目 {qid}</span>", unsafe_allow_html=True)

    # 显示完成提示（全部答完）
    if len(st.session_state.responses) == total_questions:
        st.success("🎉 恭喜，您已成功完成问卷！感谢您的参与。")
    else:
        # 主区域选择题目编号
        question_id = st.number_input("请输入题号进行作答：", min_value=1, max_value=total_questions, step=1)
        current_row = question_df[question_df["question_id"] == question_id].iloc[0]

        st.subheader(f"题目 {question_id}")
        st.markdown("请选择以下哪张图像最适合老年人步行环境：")

        col = st.columns(4)
        choice = None
        options = [current_row["image_A"], current_row["image_B"], current_row["image_C"], current_row["image_D"]]

        for i in range(4):
            with col[i]:
                st.image(os.path.join(image_root, options[i]), caption=chr(65 + i))
                if st.button(f"选择 {chr(65 + i)}", key=f"btn_{question_id}_{i}"):
                    choice = chr(65 + i)
                    st.session_state.responses[question_id] = {
                        "question_id": question_id,
                        "image_A": current_row["image_A"],
                        "image_B": current_row["image_B"],
                        "image_C": current_row["image_C"],
                        "image_D": current_row["image_D"],
                        "selected": choice,
                        "user_type": st.session_state.user_type,
                        "age_group": st.session_state.age_group if st.session_state.user_type == "elder" else "N/A"
                    }
                    st.success(f"你选择了图像 {choice}，题目 {question_id} 已完成。")

    # 保存所有已答题记录
    if st.session_state.responses:
        df = pd.DataFrame.from_dict(st.session_state.responses, orient="index")
        df.to_csv(vote_result_csv, index=False)

# --- TrueSkill 打分部分 ---
if st.sidebar.button("执行 TrueSkill 打分"):
    if os.path.exists(vote_result_csv):
        votes = pd.read_csv(vote_result_csv)
        rating_dict = {}
        env = trueskill.TrueSkill()

        for _, row in votes.iterrows():
            images = [row["image_A"], row["image_B"], row["image_C"], row["image_D"]]
            selected = row[f"image_{row['selected']}"]
            winner = selected
            losers = [img for img in images if img != winner]

            if winner not in rating_dict:
                rating_dict[winner] = env.create_rating()
            for l in losers:
                if l not in rating_dict:
                    rating_dict[l] = env.create_rating()
                rating_dict[winner], rating_dict[l] = env.rate_1vs1(rating_dict[winner], rating_dict[l])

        final_scores = pd.DataFrame(
            [(img, r.mu, r.sigma) for img, r in rating_dict.items()],
            columns=["image_path", "mu", "sigma"]
        ).sort_values("mu", ascending=False)

        st.dataframe(final_scores)
    else:
        st.warning("尚未收集到投票数据。")

