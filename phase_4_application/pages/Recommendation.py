
import streamlit as st

# Thư viện thao tác trên tập dữ liệu
import pandas as pd
import numpy as np 
pd.set_option('mode.chained_assignment', None)
from datetime import time, datetime
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt
from datetime import datetime

# Thư viện trực quan plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
st.set_option('deprecation.showPyplotGlobalUse', False)
# ---------------------- FRAME 1 -----------------------
df_titles = st.session_state.df_titles
df_credits = st.session_state.df_credits

st.header("🎞️:green[TRANG KHUYẾN NGHỊ PHIM]")
st.sidebar.markdown("# 🎞️:red[TRANG KHUYẾN NGHỊ PHIM]")

caption = "Giao diện mô tả thuật toán khuyến nghị phim cho người dùng bằng cách sử dụng phương pháp gom cụm K-Means:"
st.caption(caption, unsafe_allow_html = False)

st.markdown("### 1. Hướng dẫn sử dụng:")
caption = "Hệ thống khuyến nghị hoạt động dựa trên việc gom cụm dữ liệu sao cho ứng với các thuộc tính tính chất (type - show hay movie), năm phát hành (release year), phân loại tuổi (age certification), quốc gia sản xuất chính (main production countries) và thể loại phim."
st.write(caption)

st.markdown("#### 2. Bước 1: Vòng lặp chọn n (số lượng cụm hợp lý) nhất cho mô hình.")
caption = "Đầu tiên, ta thực hiện chọn khoảng cụm n để cho ra cụm có kết quả tốt nhất. Sau khi thực hiện xong, một biểu đồ thể hiện chỉ số inertia (chỉ số tổng bình phương khoảng cách giữa các điểm đến centroid của nó). Sau khi xem biểu đồ, ta có thể chọn được số cụm n phù hợp cho mô hình."
recommend_df = df_titles[['type', 'release_year', 'age_certification', 'main_production_countries', 'main_genre']]

genres_dict = {g: 0 for g in recommend_df['main_genre'].unique()}
countries_dict = {g: 0 for g in recommend_df['main_production_countries'].unique()}
age_dict = {g: 0 for g in recommend_df['age_certification'].unique()}
type_dict = {'SHOW': 0, 'MOVIE': 1}

idx = 0
for i,_ in genres_dict.items():
    genres_dict[i] = idx
    idx += 1

idx = 0
for i,_ in countries_dict.items():
    countries_dict[i] = idx
    idx += 1

idx = 0
for i,_ in countries_dict.items():
    age_dict[i] = idx
    idx += 1

recommend_df['main_genre'] = recommend_df['main_genre'].map(genres_dict)
recommend_df['main_production_countries'] = recommend_df['main_production_countries'].map(countries_dict)
recommend_df['age_certification'] = recommend_df['age_certification'].map(age_dict)
recommend_df['type'] = recommend_df['type'].map(type_dict)
recommend_np = recommend_df.to_numpy()

sum_distances = []

# Range values 
values_range_kmean = st.slider(
    'Chọn khoảng giá trị cần xem xét khoảng k-n',
    1, 14, (1, 14))
st.write('Values:', values_range_kmean)

K = range(values_range_kmean[0], values_range_kmean[1])

for k in K:
  k_mean = KMeans(n_clusters=k)
  k_mean.fit(recommend_np)
  sum_distances.append(k_mean.inertia_)

# plt.plot(K, sum_distances, 'bx-') 
# plt.show() 

fig1 = px.line(K, sum_distances, markers=True)
fig1 = fig1.update_layout(xaxis_title='Inerita', yaxis_title='Số cụm')
st.plotly_chart(fig1, theme=None, use_container_width=True)

# ------ CHỌN CỤM
st.markdown("#### 3. Bước 2: Chọn số n tốt từ bước 1")
n_cluster_choice = st.text_input('Nhập vào cụm n tốt nhất')

if n_cluster_choice == '':
    pass
else:
    n_cluster_choice = int(n_cluster_choice)
    k_mean = KMeans(n_clusters = n_cluster_choice)
    model = k_mean.fit(recommend_np)
    result = k_mean.labels_

    marker = ['x', 'o', 'v', '+', '.', '^', '<', '>']
    color = ['lightgreen', 'orange', 'lightblue', 'pink', 'indigo', 'cyan', 'blue', 'green']

    fig2 = plt.figure()
    for i in range(n_cluster_choice):
        plt.scatter(
            recommend_np[result == i, 1], recommend_np[result == i, -2],
            c=color[i],
            marker=marker[i], edgecolor='black',
            label='cluster ' + str(i+1)
        )

    plt.scatter(
        model.cluster_centers_[:, 1], model.cluster_centers_[:, -2],
        s=250, marker='*',
        c='red', edgecolor='black',
        label='centroids'
    )

    plt.legend(scatterpoints=1)
    fig2 = plt.grid()
    st.pyplot(fig2)

    df_titles['cluster'] = result

    def recommend(model, movie_type, release_year, age_certi, country, genre):
        arr = np.array([[movie_type, release_year, age_certi, country, genre]])
        pred = model.predict(arr)
        return df_titles[df_titles['cluster'] == pred[0]].sample(5)

    type_choice = st.selectbox(
        'Bạn thích phim (MOVIE) hay truyền hình (SHOW)',
        ('MOVIE', 'SHOW'))

    age_choice = st.selectbox(
        'Nhãn phân loại phim mà bạn quan tâm',
        ('TV-PG', 'NONE', 'PG', 'G', 'PG-13', 'R', 'TV-G', 'TV-Y', 'TV-14', 'NC-17', 'TV-Y7', 'TV-MA'))

    country_text = st.text_input('Chọn nơi sản xuất phim:')
    genre_choice = st.text_input('Chọn thể loại phim')
    release_year_choice = st.text_input('Chọn năm sản xuất')

    if len(country_text) == 0 or len(release_year_choice) == 0 or len(genre_choice) == 0:
        pass
    else:
        type_choice = type_dict[type_choice.upper()]
        age_choice = age_dict[age_choice]
        country_text = countries_dict[country_text]
        genre_choice = genres_dict[genre_choice.lower()]

        st.markdown("##### Những bộ phim bạn nên xem dựa trên lựa chọn của bạn: ")
        result = recommend(model, type_choice, release_year_choice, age_choice, country_text, genre_choice)
        st.dataframe(result, use_container_width=True)
