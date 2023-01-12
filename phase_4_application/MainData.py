# Import các thư viện cần thiết
import streamlit as st

# Thư viện thao tác trên tập dữ liệu
import pandas as pd
import numpy as np 
pd.set_option('mode.chained_assignment', None)
from datetime import time, datetime

# Thư viện trực quan plotly
import plotly.express as px

# Lấy và làm sạch dữ liệu
def loadDataCredits():
    df_netflix_credits = pd.read_csv('../data/netflix/credits.csv')
    df_amazon_credits = pd.read_csv('../data/amazon/credits.csv')
    df_hbo_credits = pd.read_csv('../data/hbo/credits.csv')

    df_credits_raw = pd.concat([df_amazon_credits, df_hbo_credits, df_netflix_credits], axis=0)

    df_credits = df_credits_raw.drop_duplicates()
    df_credits.drop('person_id', inplace=True, axis=1, errors='ignore')
    df_credits['character'] = df_credits['character'].fillna('None')

    return df_credits

def loadDataTitles():
    df_amazon_titles = pd.read_csv('../data/amazon/titles.csv')
    df_hbo_titles = pd.read_csv('../data/hbo/titles.csv')
    df_netflix_titles = pd.read_csv('../data/netflix/titles.csv')
    df_titles_raw = pd.concat([df_amazon_titles, df_hbo_titles, df_netflix_titles], axis=0)
    df_titles = df_titles_raw.drop_duplicates()

    df_titles['release_year'] = pd.to_datetime(df_titles['release_year'], format="%Y").dt.year

    df_titles.drop('description', inplace=True, axis=1)

    df_titles['age_certification'].fillna('NONE', inplace=True)

    df_titles['production_countries'] = df_titles['production_countries'].str.replace('[', '', regex=True)\
                                    .str.replace("'", '', regex=True)\
                                    .str.replace(']', '', regex=True)

    df_titles['main_production_countries'] = df_titles['production_countries'].str.split(',').str[0]

    df_titles['genres'] = df_titles['genres'].str.replace('[', '', regex=True)\
                                        .str.replace("'", '', regex=True)\
                                        .str.replace(']', '', regex=True)
                                        
    df_titles['main_genre'] = df_titles['genres'].str.split(', ').str[0]
    df_titles['seasons'] = df_titles['seasons'].fillna(0) 

    return df_titles

# Code các dataframe
df_credits = loadDataCredits()
df_titles = loadDataTitles()

# ------------------------------- FRAME 1 
st.header("📊:red[TRANG DỮ LIỆU]")
st.sidebar.markdown("# 📊:red[TRANG DỮ LIỆU]")
st.subheader("📊 0. THÔNG TIN DỮ LIỆU VÀ WEBSITE") 
caption = "Giao diện của website được xây dựng dựa trên module Streamlit, do nhóm 1 của môn Nhập môn lập trình cho khoa học dữ liệu thực hiện. \
            Website gồm có x trang chính, có các tính năng như là:"
st.caption(caption, unsafe_allow_html = False)

st.subheader("🎭 1. DỮ LIỆU CỦA CREDITS")
st.caption("Dữ liệu hiện thông tin diễn viên, đạo diễn và các nhân vật họ đã đóng.", unsafe_allow_html=False)
st.dataframe(df_credits, use_container_width=True)

# -----------------
st.markdown("---")
st.write("Sắp xếp lại thông tin dựa trên vai trò đạo diễn/diễn viên")
option = st.selectbox(
    'Xin hãy chọn vai trò',
     ['DIỄN VIÊN', 'ĐẠO DIỄN'])

if option == "DIỄN VIÊN":
    df_actor = df_credits[df_credits['role'] == "ACTOR"]
    st.dataframe(df_actor, use_container_width=True)
else: 
    df_director = df_credits[df_credits['role'] == "DIRECTOR"]
    st.dataframe(df_director, use_container_width=True)
# -----------------
st.markdown("---")
st.write("Biểu đồ thể hiện tỷ lệ giữa diễn viên và đạo diễn trên tổng số dữ liệu.")

pro_df = df_credits['role'].value_counts().rename(index='SL')

labels = ['Diễn viên', 'Đạo diễn']
fig = px.pie(pro_df, values = "SL", names=labels, title='Biểu đồ thể hiện tỷ lệ diễn viên/đạo diễn.')
st.plotly_chart(fig, theme=None, use_container_width=True)

# -----------------

st.subheader("🎬 2. DỮ LIỆU CỦA TITLES")
st.caption("Dữ liệu hiện thông tin chi tiết của các loại phim trên 3 nền tảng phân phối phim lớn như là Amazon, Netflix, HBO.", unsafe_allow_html=False)
st.dataframe(df_titles, use_container_width=True)