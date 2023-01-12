# import streamlit as st

# Thư viện thao tác trên tập dữ liệu
import pandas as pd
import numpy as np 
pd.set_option('mode.chained_assignment', None)
from datetime import time, datetime
from sklearn.cluster import KMeans
from sklearn import metrics
import matplotlib.pyplot as plt

# Thư viện trực quan plotly
import plotly.express as px

# Lấy và làm sạch dữ liệu
def loadDataCredits():
    df_netflix_credits = pd.read_csv('../../data/netflix/credits.csv')
    df_amazon_credits = pd.read_csv('../../data/amazon/credits.csv')
    df_hbo_credits = pd.read_csv('../../data/hbo/credits.csv')

    df_credits_raw = pd.concat([df_amazon_credits, df_hbo_credits, df_netflix_credits], axis=0)

    df_credits = df_credits_raw.drop_duplicates()
    df_credits.drop('person_id', inplace=True, axis=1, errors='ignore')
    df_credits['character'] = df_credits['character'].fillna('None')

    return df_credits

def loadDataTitles():
    df_amazon_titles = pd.read_csv('../../data/amazon/titles.csv')
    df_hbo_titles = pd.read_csv('../../data/hbo/titles.csv')
    df_netflix_titles = pd.read_csv('../../data/netflix/titles.csv')
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

df_titles, df_credits = loadDataTitles(), loadDataCredits()

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

# print(genres_dict)
# print(countries_dict)

recommend_df['main_genre'] = recommend_df['main_genre'].map(genres_dict)
recommend_df['main_production_countries'] = recommend_df['main_production_countries'].map(countries_dict)
recommend_df['age_certification'] = recommend_df['age_certification'].map(age_dict)
recommend_df['type'] = recommend_df['type'].map(type_dict)
recommend_np = recommend_df.to_numpy()

# print(recommend_df)

sum_distances = []
start = int(input('Start cluster: '))
end = int(input('End cluster: '))
K = range(start, end)
for k in K:
  k_mean = KMeans(n_clusters=k)
  k_mean.fit(recommend_np)
  sum_distances.append(k_mean.inertia_)

plt.plot(K, sum_distances, 'bx-')
plt.show()

n = int(input('Choose cluster: '))

k_mean = KMeans(n_clusters=n)
model = k_mean.fit(recommend_np)
result = k_mean.labels_

print('Silhouette_score', metrics.silhouette_score(recommend_np, result, metric='euclidean'))

marker = ['x', 'o', 'v', '+', '.', '^', '<', '>']
color = ['lightgreen', 'orange', 'lightblue', 'pink', 'indigo', 'cyan', 'blue', 'green']

for i in range(n):
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
plt.grid()
plt.show()

df_titles['cluster'] = result

def recommend(model, movie_type, release_year, age_certi, country, genre):
  arr = np.array([[movie_type, release_year, age_certi, country, genre]])
  pred = model.predict(arr)
  return df_titles[df_titles['cluster'] == pred[0]].sample(5)

movie_type = input('MOVIE or SHOW: ')
release_year = int(input('Choose year: '))
age_certi = input('[TV-PG, NONE, PG, G, PG-13, R, TV-G, TV-Y, TV-14, NC-17, TV-Y7, TV-MA]\nChoose age certification: ')
country = input('Choose production country (e.g US, CA, ...): ')
genre = input('Choose genre (e.g comedy, action, romance, thriller, ...): ')

movie_type = type_dict[movie_type.upper()]
age_certi = age_dict[age_certi]
country = countries_dict[country]
genre = genres_dict[genre.lower()]

print('Recommended movies:\n',recommend(model, movie_type, release_year, age_certi, country, genre))
