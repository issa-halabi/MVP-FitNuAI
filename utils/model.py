import sys
import os
import base64
from dotenv import load_dotenv
from utils.db_manager import get_unique_dishes
from openai import OpenAI
from openai.types.chat import ChatCompletion


from pydantic import BaseModel, Field
class FoodItem(BaseModel):
    food: str = Field(description="The name of the food item")
    weight: int = Field(description="The standard serving size, weight of the food item in grams, other nutrifacts are per 100 grams")
    calories: float = Field(description="The number of calories in the food item per 100 grams")
    carbs: float = Field(description="The number of carbs in the food item per 100 grams")
    fiber: float = Field(description="The number of fiber in the food item per 100 grams")
    fats: float = Field(description="The number of fats in the food item per 100 grams")
    proteins: float = Field(description="The number of proteins in the food item per 100 grams")


load_dotenv()
QUERY = '''You are a arabic-food analyzer bot created by DishAnalyzer.
When the user sends a photo, you must send the name of the food (dish or item) in the photo.
If the image contains multiple items, choose the main one.

Your final output must be one item, which is a dictionary with the following keys:
- food: The name of the food item
- weight: Always 100, representing the standard serving size of the food item in grams
- calories: The number of calories in the food item per 100 grams
- carbs: The number of carbs in the food item per 100 grams
- fiber: The number of fiber in the food item per 100 grams
- fats: The number of fats in the food item per 100 grams
- proteins: The number of proteins in the food item per 100 grams


If the item exists in the list of defined food items, it must be written in the same exact way as in this list below.
Some of the food items are main dishes, some of them are side dishes, some of them are desserts, some of them are drinks, fruits, vegetables, etc.
Here is the list of the defined food items:
{labels}

'''

class GPT_DishAnalyzer():
    def __init__(self, labels: list[str]):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        # add labels to query
        self.labels = labels
        self.query = QUERY.format(labels=', '.join(labels))

    def predict_from_base64(self, image_base64: str) -> str:
        query = self.query
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64,
                        },
                    },
                ],
            }],
            response_format=FoodItem,
        )
        decoded_output = self._decode_output(response)
        return decoded_output

    def predict(self, img_path: str) -> str:
        image_base64 = self._encode_input(img_path)
        return self.predict_from_base64(image_base64)

    def _encode_input(self, img_path: str) -> str:
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_image}"

    def _decode_output(self, response: ChatCompletion) -> str:
        # get the text from the first answer of the model
        parsed_result = response.choices[0].message.parsed
        return parsed_result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    labels = get_unique_dishes()
    analyzer = GPT_DishAnalyzer(labels=labels)
    output = analyzer.predict(image_path)
    print(output)
