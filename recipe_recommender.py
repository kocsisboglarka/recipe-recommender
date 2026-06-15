import pandas as pd

recipes = pd.read_csv("recipes.csv", encoding="latin1")

recipes = recipes.drop(columns=["cooking_time_minutes", "prep_time_minutes", "servings"])

recipes["vegan"] = False
recipes["vegetarian"] = False
recipes["gluten-free"] = False
recipes["dairy-free"] = False

count = 0
for x in recipes["dietary_restrictions"]:
    if "vegan" in str(x):
        recipes["vegan"][count] = True
    if "vegetarian" in str(x):
        recipes["vegetarian"][count] = True
    if "gluten-free" in str(x):
        recipes["gluten-free"][count] = True
    if "dairy-free" in str(x):
        recipes["dairy-free"][count] = True
    count += 1

recipes = recipes.drop(columns=["dietary_restrictions"])
