"""
This module provides a sample code to use FoodDataCentral API
"""

import requests
import dotenv
import os


dotenv.load_dotenv()

class FoodDataCentral:
    def __init__(self):
        self.api_key = os.getenv('FOODDATA_CENTRAL_API_KEY')
        self.base_url = "https://api.nal.usda.gov/fdc/v1"

    def search_foods(self, query: str, pagesize: int=1):
        params = {
            "api_key": self.api_key,
            "query": query,
            "pagesize": pagesize
        }
        response = requests.get(f"{self.base_url}/foods/search", params=params)
        return response.json()

    def get_food(self, fdc_id: str):
        params = {
            "api_key": self.api_key
        }
        response = requests.get(f"{self.base_url}/data/{fdc_id}", params=params)
        return response.json()


def get_food_nutrifatcs(food_name: str) -> dict:
    data = fdc.search_foods(food_name)['foods'][1]
    # extract calories number fron the data dict
    food_name = data['description']
    result = {'food': food_name}
    needed_nutrients = {'Energy': 'calories', 'Total lipid (fat)': 'fats', 'Carbohydrate, by difference': 'carbs', 'Protein': 'proteins', 'Fiber, total dietary': 'fiber'}
    for nutrient in data['foodNutrients']:
        if nutrient['nutrientName'] in needed_nutrients:
            nutrient_name = needed_nutrients[nutrient['nutrientName']]
            result[nutrient_name] = nutrient['value']

    result['weight'] = data['servingSize']
    print(result)


def search_foods(food_name: str, fdc: FoodDataCentral) -> dict:
    data = fdc.search_foods(food_name, pagesize=1)['foods']
    results = []
    for food in data:
        # extract calories number from the data dict
        food_name = food['description']
        result = {'food': food_name}
        needed_nutrients = {'Energy': 'calories', 'Total lipid (fat)': 'fats', 'Carbohydrate, by difference': 'carbs', 'Protein': 'proteins', 'Fiber, total dietary': 'fiber'}
        for nutrient in food['foodNutrients']:
            if nutrient['nutrientName'] in needed_nutrients:
                nutrient_name = needed_nutrients[nutrient['nutrientName']]
                result[nutrient_name] = nutrient['value']

        result['weight'] = food.get('servingSize', '')
        results.append(result)
    return results

# def search_foods(food: str, data: pd.DataFrame=None) -> dict:
#     """
#     Searches for the food in the database (non-exact search) and returns the food info.
#     """
#     if data is None:
#         data = get_all_data()
#     # non exact matching
#     food = food.lower()
#     food_columns = ['food', 'food_arabic', 'food_arabizi']
#     food_info = pd.DataFrame()
#     for column in food_columns:
#         food_info = pd.concat([food_info, data[data[column].str.contains(food, case=False, na=False)]], ignore_index=True)
#     food_info = food_info.drop_duplicates()
#     food_info.drop(columns=['food_arabic', 'food_arabizi'], inplace=True)
#     # add api data
#     fdc = FoodDataCentral()
#     api_data = search_foods_api(food, fdc)
#     api_data = pd.DataFrame(api_data)
#     food_info = pd.concat([food_info, api_data], ignore_index=True)
#     # stringify all columns
#     food_info = food_info.astype(str)
#     # subtitute null by empty string
#     food_info = food_info.fillna('')
#     return food_info.to_dict(orient='records')

if __name__ == "__main__":
    fdc = FoodDataCentral()
    results = search_foods('pizza')
    print(len(results))
