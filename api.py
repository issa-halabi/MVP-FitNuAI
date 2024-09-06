from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.db_manager import get_food_info, get_unique_dishes, get_all_data, get_data_for_gpt, search_foods, get_food_image_base64
from utils.model import GPT_DishAnalyzer, FoodItem
from utils.barcode_scanner import get_nutrition_facts


app = FastAPI()
data_for_gpt = get_data_for_gpt()
all_data = get_all_data()
unique_dishes = get_unique_dishes()
model = GPT_DishAnalyzer(labels=unique_dishes)


@app.get('/food_name/{food_name}')
async def get_nutrifacts_from_name(food_name: str):
    try:
        food_info = search_foods(food_name, all_data)
        return {'search_results': food_info}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ImageRequest(BaseModel):
    image_base64: str

@app.post('/food_image/')
async def get_nutrifacts_from_image(request: ImageRequest):
    try:
        # decode the image
        image_data = request.image_base64
        # ask model to recognize the food in image
        food_item: FoodItem = model.predict_from_base64(image_data)
        food_name = food_item.food.lower().strip()
        if food_name in unique_dishes:
            food_info = get_food_info(food_name, data_for_gpt)
            food_info['image'] = get_food_image_base64(food_name)
            food_info['gpt_based'] = False
        else:
            food_info = food_item.model_dump()
            food_info['image'] = ''
            food_info['gpt_based'] = True
        return food_info
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get('/barcode/{code}')
async def get_nutrifacts_from_barcode(code: str):
    try:
        food_info = get_nutrition_facts(code)
        return food_info
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
