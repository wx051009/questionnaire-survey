# admin.py - 管理员后台

import streamlit as st
import pandas as pd
import os

vote_result_csv = "vote_results.csv"

# --- 页面设置 ---
st.set_page_config(layout="centered")
st.title("📊 管理员后台 - 投票数据管理")

# --- 登录身份验证 ---
admin_id = st.text_input("请输入管理员昵称：")
if admin_id != "ss":
    st.error("❌ 您无权访问此页面，仅限管理员。")
    st.stop()

# --- 数据加载与预览 ---
if os.path.exists(vote_result_csv):
    df = pd.read_csv(vote_result_csv)
    df_clean = df.drop_duplicates(subset=["user_id", "question_id"], keep="last")

    st.success(f"✅ 当前共收集到 {df_clean['user_id'].nunique()} 位用户提交的答卷，总题数：{len(df_clean)}")

    with st.expander("📁 查看数据表格"):
        st.dataframe(df_clean, use_container_width=True)

    st.download_button("📥 下载去重后的投票数据", data=df_clean.to_csv(index=False), file_name="cleaned_vote_results.csv")

    # 简单统计
    st.subheader("用户组成统计")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("专家人数", int((df_clean[df_clean.user_type == "expert"]["user_id"].nunique())))
    with col2:
        st.metric("老年人数", int((df_clean[df_clean.user_type == "elder"]["user_id"].nunique())))

    st.markdown("---")
    st.write("📝 如需后续集成 TrueSkill 打分，请在此基础上上传或使用清洗后的数据。")
else:
    st.warning("尚未发现投票记录文件 vote_results.csv")
