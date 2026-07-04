# Dataset from: https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews

import pandas as pd

# I only imported the first 10 000 rows of this dataset, because it is too large to handle on its own.
recipes = pd.read_csv("recipes4.csv", nrows=10000)

# I deleted the unnecessary columns.
recipes = recipes.drop(columns=["RecipeId", "AuthorId", "AuthorName", "CookTime", "PrepTime", "DatePublished", "Description", "Images", "RecipeCategory", "AggregatedRating", "ReviewCount", "RecipeYield"])

# I wanted to know how many emptry rows were in TotalTime.
recipes["TotalTime"].isna().sum()
# I converted the TotalTime column to minutes.
parts = recipes["TotalTime"].str.extract(r"PT(?:(\d+)H)?(?:(\d+)M)?")

recipes["hours"] = parts[0].fillna(0).astype(int)
recipes["minutes"] = parts[1].fillna(0).astype(int)
recipes["total_minutes"] = recipes["hours"] * 60 + recipes["minutes"]

recipes = recipes.drop(columns=["TotalTime", "hours", "minutes"])

# I converted RecipeIngredientQuantities and RecipeIngredientParts to lists.
from io import StringIO
import csv
def convert_to_list(value):
    if pd.isna(value):
        return []

    s = str(value).strip()
    if s.startswith("c(") and s.endswith(")"):
        s = s[2:-1]
    items = next(csv.reader(StringIO(s), skipinitialspace=True))

    result = []
    for item in items:
        item = item.strip()

        if item == "NA":
            result.append("0")
        else:
            result.append(item)

    return result

recipes["RecipeIngredientQuantities"] = recipes["RecipeIngredientQuantities"].apply(convert_to_list)
recipes["RecipeIngredientParts"] = recipes["RecipeIngredientParts"].apply(convert_to_list)

# I deleted empty rows in the ingredients and parts column.
recipes = (recipes[recipes["RecipeIngredientQuantities"].str.len() > 0]).reset_index(drop=True)
recipes = (recipes[recipes["RecipeIngredientParts"].str.len() > 0]).reset_index(drop=True)

# I checked how many rows had a different number of ingredients and parts.
len_a = recipes["RecipeIngredientQuantities"].apply(len)
len_b = recipes["RecipeIngredientParts"].apply(len)
good = (len_a == len_b)
good[good==True].count()
recipes = recipes[good].reset_index(drop=True)
# Only 24% of recipes were left.
# This means that ingredients are not cleaned properly.

# I converted the Keywords and RecipeInstructions column into lists.
recipes["Keywords"] = recipes["Keywords"].apply(convert_to_list)
recipes["RecipeInstructions"] = recipes["RecipeInstructions"].apply(convert_to_list)

# I checked the keywords.
tags = set(tag for tags in recipes["Keywords"] for tag in tags)

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

recipes["cuisine"] = recipes["Keywords"].apply(classify_cuisine)

# I wanted to see how many recipes of each group there are.
recipes.groupby("cuisine").count()
# 76% of the recipes were in the unknown category.
# 0,2% were African.
# 1% were East Asian.
# 11% were European.
# 2% were Middle Eastern.
# 4% were North American.
# 4% were South American.
# 2% were South Asian.

# This means that most recipes are not categorised.

# I created the vegan column.
# There was no dairy free, gluten free or vegetarian tag so I couldn't create those columns.
recipes["vegan"] = False

for i in range(len(recipes)):
    row = recipes["Keywords"].iloc[i]

    for item in row:
        if item == "Vegan":
            recipes.loc[i, "vegan"] = True
            recipes.loc[i, "vegetarian"] = True
            
# I wanted to see how many recipes were vegan.
recipes[recipes["vegan"]==True].count()
# Only 3% of recipes were vegan.

# This means that most recipes are not categorised.

# I wanted to see how would it all look like.
cuisine = []
for x in recipes["cuisine"]:
    if x not in cuisine:
        cuisine.append(x)
cuisine = sorted(cuisine)

ingredients = set(ingredient for ingredients_list in recipes["RecipeIngredientParts"] for ingredient in ingredients_list)

import streamlit as st
st.title("Recipe Recommender")
selected_cuisine = st.selectbox("Choose a cuisine: ", cuisine)
calorie_range = st.slider("Calorie range:", 0, 2000, (100, 1900))
vegan_only = st.checkbox("Vegan")
selected_ingredients = st.multiselect("What ingredients do you have at home?", options=ingredients)

filtered_recipes = recipes[recipes["cuisine"] == selected_cuisine]

filtered_recipes = filtered_recipes[
    (filtered_recipes["Calories"] >= calorie_range[0]) &
    (filtered_recipes["Calories"] <= calorie_range[1])]

if vegan_only:
    filtered_recipes = filtered_recipes[filtered_recipes["vegan"] == True]
    
if selected_ingredients:
    matched_indexes = []

    for index, row in filtered_recipes.iterrows():
        ingredients = row["RecipeIngredientParts"]

        for selected in selected_ingredients:
            if selected in ingredients:
                matched_indexes.append(index)
                break

    filtered_recipes = filtered_recipes.loc[matched_indexes].copy()

match_counts = []

for _, row in filtered_recipes.iterrows():
    ingredients = row["RecipeIngredientParts"]

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
    with st.expander(row["Name"]):
        st.write("Cuisine:", row["cuisine"])

        st.write("Ingredients:")

        for ingredient in row["RecipeIngredientParts"]:
            if ingredient in selected_ingredients:
                st.write(f"- **:green[{ingredient}]**")
            else:
                st.write("- " + ingredient)