import sys
import os
import base64
from dotenv import load_dotenv
from utils.db_manager import get_unique_dishes
from openai import OpenAI
from openai.types.chat import ChatCompletion


load_dotenv()
QUERY = '''You are a arabic-food analyzer bot created by DishAnalyzer.
When the user sends a photo, you must send the name of the food in the photo. You must send one of those types in one line (be sure to write it in exact way):

{}

'''

class GPT_DishAnalyzer():
    def __init__(self, labels: list[str]):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        # add labels to query
        self.labels = labels
        self.query = QUERY.format(', '.join(labels))

    def predict_from_base64(self, image_base64: str) -> str:
        query = self.query
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
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
            max_tokens=300,
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
        answer = response.choices[0]
        text = answer.message.content.strip()
        if text in self.labels:
            return text
        return 'Unknown'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    labels = get_unique_dishes()
    analyzer = GPT_DishAnalyzer(labels=labels)
    output = analyzer.predict(image_path)
    print(output)
