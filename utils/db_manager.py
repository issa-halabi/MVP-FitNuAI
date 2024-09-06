import pandas as pd
import base64


def get_data_for_gpt() -> pd.DataFrame:
    """
    This function returns a pandas DataFrame with the data required for the GPT model.
    """
    df1 = pd.read_json('./data/arabic_food_db.json', dtype_backend='numpy_nullable')
    df2 = pd.read_json('./data/fruit_db.json', dtype_backend='numpy_nullable')
    df3 = pd.read_json('./data/basics.json', dtype_backend='numpy_nullable')
    df = pd.concat([df1, df2, df3], ignore_index=True)
    df['food'] = df['food'].apply(lambda x: x.lower().replace(',', ''))
    return df


def get_all_data() -> pd.DataFrame:
    """
    This function returns a DataFrame that contains all the data. (to be used for retrieval by name)
    """
    df1 = get_data_for_gpt()
    # df2 = pd.read_csv('./data/products_db.csv')
    # df = pd.concat([df1, df2], ignore_index=True)
    df = df1
    df['food'] = df['food'].apply(lambda x: x.lower())
    return df


def get_food_image_base64(food: str) -> str:
    """
    This function returns the image of the food in base64 format.
    """
    return ''
    try:
        with open(f'./data/images/{food}.jpg', 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f'Image for {food} not found')
        return 'Image not found'
    except Exception as e:
        print(f'Error getting image for {food}: {e}')
        return 'Image not found'



def get_unique_dishes(data: pd.DataFrame=None) -> list[str]:
    """Returns a list of unique dishes from the 'food_calories.json' file"""
    if data is None:
        data = get_data_for_gpt()
    return list(data['food'].unique())


def retrieve_corresponding_calories(food: str, weight: float=None, data: pd.DataFrame=None) -> int:
    """
    Retrieve the corresponding calories for a given food type and weight.
    """
    food_info = get_food_info(food, data)
    calories = food_info['calories']
    if weight:
        unit_size = food_info['weight']
        num_units = weight / unit_size
        calories = calories * num_units
    return int(calories)


def get_food_info(food: str, data: pd.DataFrame=None) -> dict:
    """
    Retrieves the food from the json file if it exists there.
    Returns: (dict) dictionary of the food
    """
    if data is None:
        data = get_all_data()
    food_columns = ['food', 'food_arabic', 'food_arabizi']
    food = food.lower()
    for column in food_columns:
        food_info = data[data[column] == food]
        if not food_info.empty:
            food_info.drop(columns=['food_arabic', 'food_arabizi'], inplace=True)
            return food_info.to_dict(orient='records')[0]
    
    raise KeyError(f'Food "{food}" does not exist in the database')


def search_foods(food: str, data: pd.DataFrame=None) -> dict:
    """
    Searches for the food in the database (non-exact search) and returns the food info.
    """
    if data is None:
        data = get_all_data()
    # non exact matching
    food = food.lower()
    food_columns = ['food', 'food_arabic', 'food_arabizi']
    food_info = pd.DataFrame()
    for column in food_columns:
        curr_food_info = data[data[column].str.contains(food, case=False, na=False)]
        curr_food_info['image'] = curr_food_info['food'].apply(get_food_image_base64)
        food_info = pd.concat([food_info, curr_food_info], ignore_index=True)
    food_info = food_info.drop_duplicates()
    food_info.drop(columns=['food_arabic', 'food_arabizi'], inplace=True)
    # stringify all columns
    food_info = food_info.astype(str)
    # subtitute null by empty string
    food_info = food_info.fillna('')
    return food_info.to_dict(orient='records')


if __name__ == '__main__':
    df = get_unique_dishes()
    print(len(df))
