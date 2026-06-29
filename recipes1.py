# Dataset from: https://www.kaggle.com/datasets/prajwaldongre/collection-of-recipes-around-the-world

# First I opened the file and made it a Pandas dataframe.
import pandas as pd
recipes = pd.read_csv("recipes1.csv", encoding="latin1")



# This can tell what columns are in the dataframe.
recipes.info()
# This can tell how many rows and columns are in the dataframe.
shape = recipes.shape



# I dropped the unnecessary columns.
recipes = recipes.drop(columns=["cooking_time_minutes", "prep_time_minutes"])



# I checked whether there are missing calories.
# There are 5.
recipes["calories_per_serving"].isna().sum()
# I deleted the rows with missing calories.
recipes = recipes[recipes["calories_per_serving"].notna()].reset_index(drop=True)
# I checked the servings columns too, but there were no missing numbers left.
recipes["servings"].isna().sum()



# For a clearer view, I split the dietary restrictions columns into 4.
recipes["vegan"] = False
recipes["vegetarian"] = False
recipes["gluten-free"] = False
recipes["dairy-free"] = False

count = 0
for x in recipes["dietary_restrictions"]:
    if "vegan" in str(x).lower():
        recipes.loc[count, "vegan"] = True
    if "vegetarian" in str(x).lower():
        recipes.loc[count, "vegetarian"] = True
    if "gluten-free" in str(x).lower():
        recipes.loc[count, "gluten-free"] = True
    if "dairy-free" in str(x).lower():
        recipes.loc[count, "dairy-free"] = True
    count += 1

recipes = recipes.drop(columns=["dietary_restrictions"])



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



# I wanted to see all the ingredients the dataset used.
ingredients = set(ingredient for ingredients_list in recipes["ingredients"] for ingredient in ingredients_list)



# All the cuisines:
cuisine = []
for x in recipes["cuisine"]:
    if x.lower() not in cuisine:
        cuisine.append(x.lower())
cuisine = sorted(cuisine)
cuisine.insert(0, "all")



# I wanted to see how would it all look like.
    # How to run Streamlit?
        # Open CMD.
        # Go to the folder where your file is saved: cd C:\Users...
        # Then run: streamlit run xyz.py
import streamlit as st
st.title("Recipe Recommender")
selected_cuisine = st.selectbox("Choose a cuisine: ", cuisine)
calorie_range = st.slider("Calorie range:", 0, 1000, (100, 900))
vegan_only = st.checkbox("Vegan")
vegetarian_only = st.checkbox("Vegetarian")
gluten_free_only = st.checkbox("Gluten-free")
dairy_free_only = st.checkbox("Dairy-free")
selected_ingredients = st.multiselect("What ingredients do you have at home?", options=ingredients)

if selected_cuisine == "all":
    filtered_recipes = recipes.copy()
else:
    filtered_recipes = recipes[recipes["cuisine"].str.lower() == selected_cuisine.lower()]

filtered_recipes = filtered_recipes[
    (filtered_recipes["calories_per_serving"] >= calorie_range[0]) &
    (filtered_recipes["calories_per_serving"] <= calorie_range[1])]

if vegan_only:
    filtered_recipes = filtered_recipes[filtered_recipes["vegan"] == True]

if vegetarian_only:
    filtered_recipes = filtered_recipes[filtered_recipes["vegetarian"] == True]

if gluten_free_only:
    filtered_recipes = filtered_recipes[filtered_recipes["gluten-free"] == True]

if dairy_free_only:
    filtered_recipes = filtered_recipes[filtered_recipes["dairy-free"] == True]
    
if selected_ingredients:
    matched_indexes = []

    for index, row in filtered_recipes.iterrows():
        ingredients = row["ingredients"]

        for selected in selected_ingredients:
            if selected in ingredients:
                matched_indexes.append(index)
                break

    filtered_recipes = filtered_recipes.loc[matched_indexes].copy()

match_counts = []

for _, row in filtered_recipes.iterrows():
    ingredients = row["ingredients"]

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
    with st.expander(row["recipe_name"]):
        st.write("Cuisine:", row["cuisine"])
        st.write("Calories per serving:", row["calories_per_serving"])

        st.write("Ingredients:")

        for ingredient in row["ingredients"]:
            if ingredient in selected_ingredients:
                st.write(f"- **:green[{ingredient}]**")
            else:
                st.write("- " + ingredient)