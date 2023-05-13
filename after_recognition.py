import requests
import json
from functools import lru_cache

global_set = set()


def getStrNutrients(original_name):
    data = get_food_info(original_name)
    food_name = data["name"]
    nutrients = data["nutrients"]

    result = "Food name: " + food_name + "\n"
    result += "\nNutrients:\n"
    for nutrient in nutrients:
        result += "\n" + str(nutrient["name"]) + ": " + str(nutrient["amount"]) + " " + str(nutrient["unit"]) + "\n"
        result += "Percent Of Daily Needs: " + str(nutrient["percentOfDailyNeeds"]) + "\n"
    return result


def getStrRecipes(original_name):
    data = get_food_info(original_name)
    food_name = data["name"]
    Recipes = data["recipes"]

    result = "<p>Food name: " + food_name + "<br>"
    result += "<br>Recipes:<br>"
    for Recipe in Recipes:
        result += "<br>" + str(Recipe["title"]) + "<br>"
        result += "<a href=" + str(Recipe["image"]) + ">The sample image</a><br></p>"
        # url = Recipe["image"]
        # result += f"<img src=\"{url}\" /img>"
        result += "<p>Used Ingredients:<br>" + str(Recipe["usedIngredients"]) + "<br>"
        result += "Missed Ingredients:<br>" + str(Recipe["missedIngredients"]) + "<br>"
        result += "Unused Ingredients:<br>" + str(Recipe["unusedIngredients"]) + "<br>"
        result += "likes:" + str(Recipe["likes"]) + "<br>"
    result += "</p>"
    return result


def get_food_info(original_name):
    food_status = "Fresh"
    toxicity = {}
    # handle possible prefix
    if original_name.startswith("Fresh"):
        food_name = original_name.removeprefix("Fresh")
        global_set.add(food_name)
    elif original_name.startswith("Rotten"):
        food_name = original_name.removeprefix("Rotten")
        food_status = "Rotten"
        toxicity = query_toxicity(food_name)
        if toxicity is None:
            toxicity = {}
    else:
        food_name = original_name
        global_set.add(food_name)

    name = (food_status + " " + food_name).strip()
    # query bing image API
    image_url = query_image_from_bing(name)

    # query food nutrients
    nutrients = query_from_spoonacular(food_name)
    if nutrients is None:
        # try to get from another data source
        nutrients = query_from_edamam(food_name)
    else:
        # if no image from bing, then use image from Spoonacular
        if image_url is None or len(image_url) == 0:
            image_url = nutrients["image_url"]

    # recipes
    frozen_set = frozenset(global_set)
    recipes = query_recipes(frozen_set)
    if recipes is None:
        recipes = []

    return {
        "name": name,
        "nutrients": nutrients["nutrients"],
        "image_url": image_url,
        "recipes": recipes,
        "toxicity": toxicity
    }


@lru_cache(maxsize=64)
def query_image_from_bing(name):
    # use bing to search standard image
    bing_image_search_api_key = "8ba9386d8c4047a294aecb99a401c8f0"
    bing_image_search_url = f"https://api.bing.microsoft.com/v7.0/images/search" \
                            f"?q={name}&count=1&size=medium&imageType=photo"

    headers = {
        "Ocp-Apim-Subscription-Key": bing_image_search_api_key
    }

    # query bing image API
    response = requests.get(bing_image_search_url, headers=headers)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        image_url = response_data["value"][0]["contentUrl"]
        return image_url

    return None


@lru_cache(maxsize=64)
def query_toxicity(name):
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": "8ba9386d8c4047a294aecb99a401c8f0"}
    query = "will I get sick if I eat rotten " + name

    response = requests.get(endpoint, headers=headers, params={"q": query})
    if response.status_code == 200:
        data = json.loads(response.text)
        snippet = data["webPages"]["value"][0]["snippet"]
        return snippet

    return None


@lru_cache(maxsize=64)
def query_recipes(param_set):  # use set as param to enable cache correctly
    response_data = {}
    if len(param_set) == 0:
        return response_data
    ingredients = ','.join(param_set)
    # Spoonacular API
    spoonacular_api_key = "f4f80a8a101c42139dcbecca2cda7b0f"
    spoonacular_search_url = f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={spoonacular_api_key}" \
                             f"&ingredients={ingredients}&number=5&ignorePantry=true&ranking=2&limitLicense=true"

    response = requests.get(spoonacular_search_url)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        return response_data

    return None


@lru_cache(maxsize=64)
def query_from_spoonacular(food_name):
    # Spoonacular API
    spoonacular_api_key = "f4f80a8a101c42139dcbecca2cda7b0f"
    spoonacular_search_url = f"https://api.spoonacular.com/food/ingredients/search?query={food_name}" \
                             f"&metaInformation=true&number=1&apiKey={spoonacular_api_key}"

    response = requests.get(spoonacular_search_url)
    if response.status_code == 200:
        response_data = json.loads(response.text)

        if len(response_data["results"]) != 0:
            product_id = response_data["results"][0]["id"]

            spoonacular_info_url = f"https://api.spoonacular.com/food/ingredients/{product_id}/information?" \
                                   f"amount=100&unit=grams&apiKey={spoonacular_api_key}"
            response = requests.get(spoonacular_info_url)
            response_data = json.loads(response.text)

            return {
                "nutrients": response_data["nutrition"]["nutrients"],
                "image_url": "https://spoonacular.com/cdn/ingredients_500x500/" + response_data["image"]
            }

    return None


@lru_cache(maxsize=64)
def query_from_edamam(food_name):
    url = f"https://api.edamam.com/api/nutrition-data?app_id=69ea3e0f&app_key=3775db1d3a1bce8ccc79453e739c0ead" \
          f"&ingr=100g {food_name}"
    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()
        total_nutrients = data["totalNutrients"]
        total_daily = data["totalDaily"]
        # merge information
        for key in total_nutrients.keys():
            if key in total_daily:
                total_nutrients[key]["percentOfDailyNeeds"] = total_daily[key]["quantity"]
            else:
                total_nutrients[key]["percentOfDailyNeeds"] = "N/A"

        diet_labels = data["dietLabels"]
        cautions = data["cautions"]

        return {
            "nutrients": total_nutrients,
            "dietLabels": diet_labels,
            "cautions": cautions
        }

    else:
        return None


if __name__ == "__main__":
    query_toxicity("potato")
    food_info = get_food_info("Banana")
    # result = json.dumps(food_info, ensure_ascii=False)
    # result = getStrRecipes("Banana")
    # result=getStrNutrients("Banana")
    print(food_info)
