import streamlit as st
import mlfoundry
import pandas as pd

from scipy.sparse import coo_matrix

@st.cache(allow_output_mutation=True)
def load_models_and_dfs():
  client = mlfoundry.get_client("https://app.develop.truefoundry.tech/api/ml")
  run = client.get_run('truefoundry/user-truefoundry/rexx/organic-serval')
  model = client.get_model("model:truefoundry/user-truefoundry/rexx/rexx-implicit:1").load()


  movies_local_path = run.download_artifact('movies_metadata.csv')
  ratings_local_path = run.download_artifact('ratings_small.csv')

  movie_meta_df = pd.read_csv(movies_local_path)
  ratings_df = pd.read_csv(ratings_local_path)
  
  ratings_df['movieId_cat'] = ratings_df['movieId'].astype("category")
  ratings_df['userId_cat'] = ratings_df['userId'].astype("category")

  ratings = ratings_df['rating']
  rows = ratings_df['userId_cat'].cat.codes
  cols = ratings_df['movieId_cat'].cat.codes

  sparse_matrix = coo_matrix((ratings, (rows, cols)))
  return model, sparse_matrix, movie_meta_df, ratings_df

model, sparse_matrix, movie_meta_df, ratings_df = load_models_and_dfs()

@st.cache(allow_output_mutation=True)
def get_movie_id_from_cat_code(cat_code):
  return ratings_df['movieId_cat'].cat.categories[cat_code]

@st.cache(allow_output_mutation=True)
def get_user_id_from_cat_code(cat_code):
  return ratings_df['userId_cat'].cat.categories[cat_code]

@st.cache(allow_output_mutation=True)
def get_cat_code_from_user_id(user_id):
  return ratings_df['userId_cat'].cat.categories.get_loc(user_id)

@st.cache(allow_output_mutation=True)
def get_cat_code_from_movie_id(movie_id):
  return ratings_df['movieId_cat'].cat.categories.get_loc(movie_id)

def get_recommendation_for_user(user_id):
  user_cat_code = get_cat_code_from_user_id(user_id)
  return [get_movie_id_from_cat_code(cat_code) for cat_code in model.recommend(user_cat_code, sparse_matrix.tocsr().getrow(user_cat_code))[0]]
  
def get_movie_names_for_movie_ids(movie_ids):
    return list(movie_meta_df.loc[movie_meta_df['id'].isin([str(id) for id in movie_ids])].original_title)


st.title('Movie recommendations')
user_id = st.selectbox('Enter User Id', list(ratings_df['userId'].unique()))
st.write('Recommendations for user')
for movie_id in get_movie_names_for_movie_ids(get_recommendation_for_user(user_id)):
    st.markdown("- " + movie_id)