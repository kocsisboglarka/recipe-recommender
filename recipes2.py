# Dataset from: https://www.kaggle.com/datasets/realalexanderwei/food-com-recipes-with-ingredients-and-tags

import pandas as pd

# This file has over 500 000 rows, which makes it slower to process.
# So I only import the first 10 000 rows.
recipes = pd.read_csv("recipes2.csv", nrows=10000, encoding="utf-8")

# After looking at the columns, I deleted the unnecessary ones.
recipes.info()
recipes = recipes.drop(columns=["id", "serving_size", "description"])



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

# I repeated the same steps with the rwa ingredients and tags.
type(recipes["ingredients_raw"].iloc[0])
recipes["ingredients_raw"] = recipes["ingredients_raw"].apply(convert_to_list)

type(recipes["tags"].iloc[0])
recipes["tags"] = recipes["tags"].apply(convert_to_list)


# I wanted to know whether there are rows with no ingredients.
# There were 244. I deleted them.
empty_ingredients_count = 0
for ingredients in recipes["ingredients"]:
    if ingredients == []:
        empty_ingredients_count += 1

recipes = (recipes[recipes["ingredients"].str.len() > 0]).reset_index(drop=True)

# I did the same with the raw ingredients.
# But there were none.
empty_ingredients_count = 0
for ingredients in recipes["ingredients_raw"]:
    if ingredients == []:
        empty_ingredients_count += 1
        
# I noticed that recipes with less then 3 ingredients were mostly wrong.
# So I deleted them.
recipes = (recipes[recipes["ingredients"].apply(len) > 2]).reset_index(drop=True)


# I deleted all the rows where the number of ingredients didn't match the number of raw ingredients.
# With only this step, 73% of recipes were deleted.
len_ing = recipes["ingredients"].apply(len)
len_raw = recipes["ingredients_raw"].apply(len)
good = (len_ing == len_raw)
recipes = recipes[good].reset_index(drop=True)


# I wanted to see all the tags.
tags = set(tag for tags in recipes["tags"] for tag in tags)


# I created the cuisine columns based on what is in the tags column.
def classify_cuisine(tags):
    tags = [tag.lower().strip() for tag in tags]

    east_asian = [
        "chinese", "korean", "japanese", "thai", "vietnamese", "mongolian", "chinese-new-year",
        "taiwanese", "hong kong", "hongkongese", "macanese", "east-asian", "east asian",
        "soy-tofu", "szechuan"
    ]

    south_asian = [
        "indian", "pakistani", "bangladeshi", "sri lankan", "nepalese",
        "bhutanese", "maldivian", "south-asian", "south asian", "laotian",
        "micro-melanesia", "new-zealand", "polynesian"
    ]

    middle_eastern = [
        "middle eastern", "persian", "iranian", "iraqi", "lebanese", "turkish", "hanukkah",
        "syrian", "israeli", "palestinian", "jordanian", "saudi", "saudi arabian", "iranian-persian",
        "emirati", "yemeni", "omani", "qatari", "kuwaiti", "bahraini", "middle-eastern",
        "jewish-ashkenazi", "jewish-sephardi", "kosher", "non-alcoholic", "ramadan", "rosh-hashana",
        "rosh-hashanah", "saudi-arabian"
    ]

    african = [
        "african", "ethiopian", "eritrean", "somali", "sudanese", "south sudanese",
        "egyptian", "libyan", "tunisian", "algerian", "moroccan", "nigerian",
        "ghanaian", "senegalese", "ivorian", "cameroonian", "kenyan", "ugandan",
        "tanzanian", "rwandan", "burundian", "angolan", "mozambican",
        "botswanan", "namibian", "zambian", "zimbabwean", "south african",
        "malagasy", "south-african"
    ]

    european = [
        "european", "italian", "french", "greek", "spanish", "portuguese",
        "german", "austrian", "swiss", "belgian", "dutch", "luxembourgish",
        "british", "english", "scottish", "welsh", "irish", "icelandic",
        "norwegian", "swedish", "danish", "finnish", "estonian", "latvian",
        "lithuanian", "polish", "czech", "slovak", "hungarian", "romanian",
        "bulgarian", "croatian", "serbian", "bosnian", "slovenian",
        "montenegrin", "macedonian", "albanian", "kosovan", "moldovan",
        "ukrainian", "belarusian", "russian", "scandinavian", "spaghetti", "pizza", "lagagne",
        "lasagna", "st-patricks-day"
    ]

    north_american = [
        "american", "united states", "u.s.", "u.s.a.", "usa", "canadian",
         "british-columbian", "amish-mennonite", "native-american", "quebec",
         "north-american", "north american", "memorial-day", "midwestern",
         "northeastern-united-states", "ontario", "pacific-northwest", "pennsylvania-dutch",
         "south-west-pacific", "southern-united-states", "southwestern-united-states",
         "super-bowl", "superbowl", "thanksgiving"
    ]

    south_american = [
        "south american", "argentine", "argentinian", "bolivian", "brazilian",
        "chilean", "colombian", "ecuadorean", "ecuadorian", "guyanese", "oaxacan",
        "paraguayan", "peruvian", "surinamese", "uruguayan", "venezuelan", "south-american",
        "mexican", "cuban", "jamaican", "haitian", "dominican", "puerto rican",
        "trinidadian", "barbadian", "bahamian", "belizean", "guatemalan", "central-american",
        "honduran", "salvadoran", "nicaraguan", "costa rican", "panamanian", "caribbean", 
        "puerto-rican", "salsas", "south-american", "tex-mex"
    ]

    for tag in tags:
        if tag in east_asian:
            return "east_asian"
        if tag in south_asian:
            return "south_asian"
        if tag in middle_eastern:
            return "middle_eastern"
        if tag in african:
            return "african"
        if tag in european:
            return "european"
        if tag in north_american:
            return "north_american"
        if tag in south_american:
            return "south_american"

    return "unknown"

recipes["cuisine"] = recipes["tags"].apply(classify_cuisine)

# I wanted to see how many recipes of each group there are.
recipes.groupby("cuisine").count()
# 61% of the recipes were in the unknown category.
# 0,8% were African.
# 2% were East Asian.
# 9% were European.
# 1% were Middle Eastern.
# 22% were North American.
# 1% were South American.
# 0,6% were South Asian.

# This means that most recipes are not categorised.



# I created the vegan, gluten-free and vegetarian column.
# There was no dairy free tag, so I couldn't create that column.
recipes["vegan"] = False
recipes["vegetarian"] = False
recipes["gluten-free"] = False

for i in range(len(recipes)):
    row = recipes["tags"].iloc[i]

    for item in row:
        if item == "gluten-free":
            recipes.loc[i, "gluten-free"] = True
        if item == "vegan":
            recipes.loc[i, "vegan"] = True
            recipes.loc[i, "vegetarian"] = True

        elif item == "vegetarian":
            recipes.loc[i, "vegetarian"] = True
            
# I wanted to see how many recipes of each group there are.
recipes[recipes["vegan"]==True].count()
recipes[recipes["vegetarian"]==True].count()
recipes[recipes["gluten-free"]==True].count()
# Only 5% of recipes were vegan, 2% were gluten free and 15% were vegetarian.

# This means that most recipes are not categorised.




# I wanted to see how would it all look like.
cuisine = []
for x in recipes["cuisine"]:
    if x not in cuisine:
        cuisine.append(x)
cuisine = sorted(cuisine)

ingredients = set(ingredient for ingredients_list in recipes["ingredients"] for ingredient in ingredients_list)

import streamlit as st
st.title("Recipe Recommender")
selected_cuisine = st.selectbox("Choose a cuisine: ", cuisine)
vegan_only = st.checkbox("Vegan")
vegetarian_only = st.checkbox("Vegetarian")
gluten_free_only = st.checkbox("Gluten-free")
selected_ingredients = st.multiselect("What ingredients do you have at home?", options=ingredients)

filtered_recipes = recipes[recipes["cuisine"] == selected_cuisine]

if vegan_only:
    filtered_recipes = filtered_recipes[filtered_recipes["vegan"] == True]

if vegetarian_only:
    filtered_recipes = filtered_recipes[filtered_recipes["vegetarian"] == True]

if gluten_free_only:
    filtered_recipes = filtered_recipes[filtered_recipes["gluten-free"] == True]
    
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
    with st.expander(row["name"]):
        st.write("Cuisine:", row["cuisine"])

        st.write("Ingredients:")

        for ingredient in row["ingredients"]:
            if ingredient in selected_ingredients:
                st.write(f"- **:green[{ingredient}]**")
            else:
                st.write("- " + ingredient)