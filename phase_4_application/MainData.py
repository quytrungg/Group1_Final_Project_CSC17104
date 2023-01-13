# Import các thư viện cần thiết
import streamlit as st

# Thư viện thao tác trên tập dữ liệu
import pandas as pd
import numpy as np 
pd.set_option('mode.chained_assignment', None)
from datetime import time, datetime

# Thư viện trực quan plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(
    page_title="MainData",
    page_icon='📊',
)

# Share tiến trình
if "df_credits" or "df_titles" not in st.sesstion_state:
    st.session_state.df_credits = None
    st.session_state.df_titles = None

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

caption = "Giao diện của website được xây dựng dựa trên module Streamlit, do nhóm 1 của môn Nhập môn lập trình cho khoa học dữ liệu thực hiện. \
            Website gồm có x trang chính, có các tính năng như là:"
st.caption(caption, unsafe_allow_html = False)

st.markdown('<h3 style="text-align: center;"> 🎭 1. DỮ LIỆU CỦA CREDITS </p>', unsafe_allow_html=True)
st.caption("Dữ liệu hiện thông tin diễn viên, đạo diễn và các nhân vật họ đã đóng.", unsafe_allow_html=False)
st.dataframe(df_credits, use_container_width=True)

# -----------------
st.markdown("---")
st.markdown(":green[**TÁC VỤ 1**: Tra cứu tên diễn viên, đạo diễn]")

tit = st.text_input('Nhập tên diễn viên/đạo diễn')
st.write('Sau đây là các kết quả của diễn viên/đạo diễn: ', tit)

if tit == '':
    pass
else:
    result_df = df_credits[df_credits['name'].str.contains(tit)]
    st.dataframe(result_df, use_container_width=True)

# ------------------
st.markdown("---")
st.markdown(":green[**TÁC VỤ 2**: Sắp xếp lại thông tin dựa trên vai trò đạo diễn/diễn viên.]")

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
st.markdown(":green[**TÁC VỤ 3**: Biểu đồ thể hiện tỷ lệ giữa diễn viên và đạo diễn trên tổng số dữ liệu.]")

pro_df = df_credits['role'].value_counts().rename(index='SL')

labels_dv_dd = ['Diễn viên', 'Đạo diễn']
fig = px.pie(pro_df, values = "SL", names=labels_dv_dd, title='Biểu đồ thể hiện tỷ lệ diễn viên/đạo diễn.')
st.plotly_chart(fig, theme=None, use_container_width=True)

# ---------------------------------------------------------------------------------------------------

st.markdown('<h3 style="text-align: center;"> 🎬 2. DỮ LIỆU CỦA TITLES </p>', unsafe_allow_html=True)
st.caption("Dữ liệu hiện thông tin chi tiết của các loại phim trên 3 nền tảng phân phối phim lớn như là Amazon, Netflix, HBO.", unsafe_allow_html=False)
st.dataframe(df_titles, use_container_width=True)


st.markdown("---")
st.markdown(":green[**TÁC VỤ 1**: Phân phối các dữ liệu thuộc tính số]")

# ----XỬ LÝ THUỘC TÍNH SỐ ------
def missing_ratio(c):
    return c.isnull().sum() / c.__len__() * 100

def lower_quantile(column):
    return column.quantile(q = 0.25)

def upper_quantile(column):
    return column.quantile(q = 0.75)

def mean(column):
    return column.mean()

def median(column):
    return column.median()

# ----LẤY CỘT SỐ VÀ TÍNH ------
plotThis = df_titles[df_titles.describe().columns].agg([missing_ratio, min, lower_quantile,  
                                                    median, upper_quantile, max, mean]).round(1)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Năm phát hành", "Thời lượng", "Số mùa", "Điểm IMDB", 
                                                    "Số đánh giá IMDB", "Độ phổ biến TMDB", "Điểm TMDB"])

labelsBarChart = ['Missing ratio', 'Min', 'Lower quantile', 'Median', 'Upper quantile', 'Max', 'Mean']

with tab1:
    fig1 = px.bar(plotThis, x='release_year', y = labelsBarChart, title='Phân phối thuộc tính của cột năm phát hành (Release year)',
                text=plotThis['release_year'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='Year')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab2:
    fig1 = px.bar(plotThis, x='runtime', y = labelsBarChart, title='Phân phối thuộc tính của cột thời lượng (Runtime)',
                text=plotThis['runtime'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='runtime')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab3:
    fig1 = px.bar(plotThis, x='seasons', y = labelsBarChart, title='Phân phối thuộc tính của cột số mùa (Seasons)',
                text=plotThis['seasons'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='seasons')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab4:
    fig1 = px.bar(plotThis, x='imdb_score', y = labelsBarChart, title='Phân phối thuộc tính của điểm IMDB (IMDB score)',
                text=plotThis['imdb_score'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='imdb_score')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab5:
    fig1 = px.bar(plotThis, x='imdb_votes', y = labelsBarChart, title='Phân phối thuộc tính của điểm đánh giá IMDB (IMDB votes)',
                text=plotThis['imdb_votes'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='imdb_votes')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab6:
    fig1 = px.bar(plotThis, x='tmdb_popularity', y = labelsBarChart, title='Phân phối thuộc tính độ phổ biến IMDB (IMDB popularity)',
                text=plotThis['tmdb_popularity'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='tmdb_popularity')
    st.plotly_chart(fig1, theme=None, use_container_width=True)

with tab7:
    fig1 = px.bar(plotThis, x='tmdb_score', y = labelsBarChart, title='Phân phối thuộc tính điểm TMDB (TMDB Score)',
                text=plotThis['tmdb_score'].iloc[:])
    fig1 = fig1.update_layout(xaxis_title='tmdb_score')
    st.plotly_chart(fig1, theme=None, use_container_width=True)


st.markdown("---")
st.markdown(":green[**TÁC VỤ 2**: Trực quan tỷ lệ phần trăm của show/movie trên tổng dữ liệu]")

pro_df_title = df_titles['type'].value_counts().rename(index='SL')

labels = ['MOVIE', 'SHOW']
fig2 = px.pie(pro_df_title, values = "SL", names=labels, title='Biểu đồ thể hiện tỷ lệ show/phim.')
st.plotly_chart(fig2, theme=None, use_container_width=True)


st.markdown("---")
st.markdown(":green[**TÁC VỤ 3**: Trực quan lượng phim qua các năm]")
num_of_movies_by_year = df_titles['release_year'].value_counts().sort_index().rename(index="Số lượng phim")
fig3 = px.bar(num_of_movies_by_year)
fig3 = fig3.update_layout(xaxis_title='Năm phát hành')
st.plotly_chart(fig3, theme=None, use_container_width=True)

st.markdown("---")
st.markdown(":green[**TÁC VỤ 3**: Trực quan phần trăm các nhãn độ tuổi được gán cho phim]")
age_cert = df_titles['age_certification'].value_counts()

labelFig4 = ['NONE', 'R', 'PG-13', 'TV-MA', 'PG', 'TV-14', 'G', 'TV-PG', 'TV-Y7', 'TV-Y', 'TV-G', 'NC-17']

fig4 = px.pie(age_cert, values = "age_certification", names=labelFig4)
st.plotly_chart(fig4, theme=None, use_container_width=True)


st.markdown("---")
st.markdown(":green[**TÁC VỤ 4**: Xem n quốc gia lọt top sản xuất nhiều phim nhất]")
top_production_countries = df_titles['production_countries'].str.split(', ').explode().value_counts().drop('')
num_production_countries = df_titles['production_countries'].str.split(',').explode().nunique()

top_n = st.text_input('Nhập số n (top) mà bạn muốn kiếm tra')
st.write('Sau đây là các kết quả top: ', top_n)

if top_n == '':
    pass
else:
    top_frame = top_production_countries.nlargest(int(top_n));
    st.dataframe(top_frame, use_container_width=True)


st.session_state.df_credits = df_credits
st.session_state.df_titles = df_titles