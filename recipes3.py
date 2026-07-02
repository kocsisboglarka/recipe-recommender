# Dataset from: https://www.kaggle.com/datasets/wilmerarltstrmberg/recipe-dataset-over-2m

import pandas as pd

# I only imported the first 10 000 rows of this dataset, because it is too large to handle on its own.
# This dataset has more than 2 million recipes.
recipes = pd.read_csv("recipes3.csv", nrows=10000, encoding="latin1")

# I deleted the unnecessary columns.
recipes = recipes.drop(columns=["link", "site", "source"])

# I checked whether the ingredients columns contains lists or basic strings.
# It turned out, that they just looked like lists, but were actually strings.
type(recipes["ingredients"].iloc[0])
# I converted them to true lists.
import ast

def convert_to_list(value):
    if pd.isna(value):
        return []
    if isinstance(value, str):
        return ast.literal_eval(value)
    return value
recipes["ingredients"] = recipes["ingredients"].apply(convert_to_list)

# I repeated the same steps with the raw ingredients and instructions.
type(recipes["NER"].iloc[0])
recipes["NER"] = recipes["NER"].apply(convert_to_list)

type(recipes["directions"].iloc[0])
recipes["directions"] = recipes["directions"].apply(convert_to_list)



# I wanted to know whether there are rows with no directions.
# There were none.
empty_row_count = 0
for rows in recipes["directions"]:
    if rows == []:
        empty_row_count += 1

# I repeated the same with ingredients.
# There were none.
empty_row_count = 0
for rows in recipes["ingredients"]:
    if rows == []:
        empty_row_count += 1
        
# I deleted all recipes with less than 3 ingredients, because they were mostly incorrect.
# Only 1% of the recipes were deleted this way.
recipes = (recipes[recipes["ingredients"].apply(len) > 2]).reset_index(drop=True)


# I checked how many rows had a different number of ingredients and raw ingredients.
len_ing = recipes["ingredients"].apply(len)
len_raw = recipes["NER"].apply(len)
good = (len_ing == len_raw)
good[good==True].count()
# 80% of recipes were correct.
# This suggests that ingredients are not cleaned properly.
recipes = recipes[good].reset_index(drop=True)



# I wanted to see all the cleaned ingredients.
ingredients = set(ingredient for ingredients in recipes["NER"] for ingredient in ingredients)


# I wanted to see how would it all look like.
import streamlit as st
st.title("Recipe Recommender")
selected_ingredients = st.multiselect("What ingredients do you have at home?", options=ingredients)
    
filtered_recipes = recipes
if selected_ingredients:
    matched_indexes = []

    for index, row in filtered_recipes.iterrows():
        ingredients = row["NER"]

        for selected in selected_ingredients:
            if selected in ingredients:
                matched_indexes.append(index)
                break

    filtered_recipes = filtered_recipes.loc[matched_indexes].copy()

match_counts = []

for _, row in filtered_recipes.iterrows():
    ingredients = row["NER"]

    count = 0

    for selected in selected_ingredients:
        if selected in ingredients:
            count += 1

    match_counts.append(len(ingredients) - count)


filtered_recipes["match_count"] = match_counts

filtered_recipes = filtered_recipes.sort_values(
    by="match_count",
    ascending=True
)

st.subheader("Matching recipes")

for _, row in filtered_recipes.iterrows():
    with st.expander(row["title"]):

        st.write("Ingredients:")

        for ingredient in row["NER"]:
            if ingredient in selected_ingredients:
                st.write(f"- **:green[{ingredient}]**")
            else:
                st.write("- " + ingredient)