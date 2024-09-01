from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.db_manager import get_food_info, get_unique_dishes, get_all_data, get_data_for_gpt, search_foods
from utils.model import GPT_DishAnalyzer
from utils.barcode_scanner import parse_barcode_image_base64, get_nutrition_facts, ScannerException


app = FastAPI()
data_for_gpt = get_data_for_gpt()
all_data = get_all_data()
model = GPT_DishAnalyzer(labels=get_unique_dishes(data_for_gpt))


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
        food_name = model.predict_from_base64(image_data)
        food_info = get_food_info(food_name, data_for_gpt)
        return food_info
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post('/barcode_image/')
async def get_nutrifacts_from_barcode(request: ImageRequest):
    try:
        image_data = request.image_base64
        code = parse_barcode_image_base64(image_data)
        food_info = get_nutrition_facts(code)
        return food_info
    except ScannerException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
