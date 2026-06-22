import pandas as pd
import streamlit as st

df = pd.read_csv("recipes_data.csv", nrows=5, encoding="latin1")
print(df["ingredients"].iloc[0])
print(type(df["ingredients"].iloc[0]))

st.title("Recipe Recommender")

recipes = pd.read_csv("recipes.csv", encoding="latin1")

recipes = recipes.drop(columns=["cooking_time_minutes", "prep_time_minutes", "servings"])

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

ingredients = []
for y in recipes["ingredients"]:
    text = str(y)
    text = text.replace("[", "")
    text = text.replace("]", "")
    ingredient = text.split("', '")
    for z in ingredient:
        z = z.strip().lower().replace("'", "")
        if z not in ingredients:
            ingredients.append(z)

ingredients = sorted(ingredients)
ingredients.remove('water, "zaatar spice blend (sesame seeds, sumac, thyme)", cheese (akawi or mozzarella)')

cuisine = []
for a in recipes["cuisine"]:
    if a.lower() not in cuisine:
        cuisine.append(a.lower())
cuisine = sorted(cuisine)
cuisine.insert(0, "all")

selected_cuisine = st.selectbox("Choose a cuisine: ", cuisine)

calorie_range = st.slider("Calorie range:", 0, 1000, (100, 900))

vegan_only = st.checkbox("Vegan")
vegetarian_only = st.checkbox("Vegetarian")
gluten_free_only = st.checkbox("Gluten-free")
dairy_free_only = st.checkbox("Dairy-free")

selected_ingredients = st.multiselect(
    "What ingredients do you have at home?", options=ingredients)

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
    matched_rows = []

    for _, row in filtered_recipes.iterrows():
        text = str(row["ingredients"])
        text = text.replace("[", "").replace("]", "")
        ingredient_list = text.split("', '")

        cleaned_ingredients = []
        for ingredient in ingredient_list:
            ingredient = ingredient.strip().lower().replace("'", "")
            cleaned_ingredients.append(ingredient)

        for selected in selected_ingredients:
            if selected.lower() in cleaned_ingredients:
                matched_rows.append(row)
                break

    filtered_recipes = pd.DataFrame(matched_rows)

match_counts = []

for _, row in filtered_recipes.iterrows():
    text = str(row["ingredients"])
    text = text.replace("[", "").replace("]", "")
    ingredient_list = text.split("', '")

    cleaned_ingredients = []
    for ingredient in ingredient_list:
        ingredient = ingredient.strip().lower().replace("'", "")
        cleaned_ingredients.append(ingredient)

    count = 0
    for selected in selected_ingredients:
        if selected.lower() in cleaned_ingredients:
            count += 1

    match_counts.append(len(cleaned_ingredients) - count)

filtered_recipes["match_count"] = match_counts
filtered_recipes = filtered_recipes.sort_values(by="match_count", ascending=True)

st.subheader("Maching recipes")

for _, row in filtered_recipes.iterrows():
    with st.expander(row["recipe_name"]):
        st.write("Cuisine:", row["cuisine"])
        st.write("Calories per serving:", row["calories_per_serving"])
        
        text = str(row["ingredients"])
        text = text.replace("[", "").replace("]", "")
        ingredient_list = text.split("', '")
        
        st.write("Ingredients:")
        for ingredient in ingredient_list:
            ingredient = ingredient.strip().replace("'", "").lower()
            if ingredient in selected_ingredients:
                st.write(f"- **:green[{ingredient}]**")
            else:
                st.write("- " + ingredient)
