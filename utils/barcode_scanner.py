import cv2
from cv2.typing import MatLike
from pyzbar.pyzbar import decode
from zxing import BarCodeReader
from PIL import Image
import numpy as np
import base64
import openfoodfacts
import requests



class ScannerException(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


api = openfoodfacts.API(user_agent="ExampleAgentName")
# get details about an item
def get_nutrition_facts(code: str) -> dict:
    """
    Get nutrition facts for a given code.
    """
    product_data = api.product.get(code, fields=["code", "product_name", "nutriments", "image_url"])
    if not product_data:
        raise KeyError(f"Product of code {code} not found in database.")
    nutriments = product_data['nutriments']
    image_url = product_data.get('image_url')
    image = get_food_image_base64(image_url)
    return {
        'food': product_data.get('product_name'),
        'weight': '100',
        # get calories from energy-kcal or convert it from kj, 1 kcal is 4.184 kj
        'calories': nutriments.get('energy-kcal_100g') or nutriments.get('energy-kcal') or round(nutriments.get('energy', 0) / 4.184),
        'fat': nutriments.get('fat_100g'),
        'carbohydrates': nutriments.get('carbohydrates_100g'),
        'protein': nutriments.get('proteins_100g'),
        'image': image
    }


def get_food_image_base64(image_url: str) -> str:
    """
    Get the image of the food in base64 format.
    """
    return ''
    # Download the image if available
    if image_url:
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image = image_response.content
            image = base64.b64encode(image).decode('utf-8')
            return image
    return 'Image not found'


def parse_barcode_image(image: MatLike) -> str:
    """
    Parse a barcode image and return the barcode value.
    """
    detectedBarcodes = decode(image)
    if not detectedBarcodes:
        raise ScannerException("Barcode Not Detected or your barcode is blank/corrupted!")
    barcode = detectedBarcodes[0]
    if barcode.data == "":
        raise ScannerException('Barcode contains no data!')
    return barcode.data.decode("utf-8")


def parse_barcode_image_path(image_path: str) -> str:
    """
    Parse a barcode image from a file path and return the barcode value.
    """
    image = cv2.imread(image_path)
    try:
        result = parse_barcode_image(image)
    # if pyzbar fails, try pyzxing
    except ScannerException:
        result = alternative_barcode_parser(image_path)
    return result


def parse_barcode_image_base64(image_base64: str) -> str:
    """
    Parse a barcode image from a base64 string and return the barcode value
    """
    if image_base64.startswith('data:image/'):
        image_base64 = image_base64.split(',', 1)[1]
    image_matlike = cv2.imdecode(np.frombuffer(base64.b64decode(image_base64), np.uint8), cv2.IMREAD_COLOR)
    try:
        result = parse_barcode_image(image_matlike)
    # if pyzbar fails, try pyzxing
    except ScannerException:
        # pyzxing needs image as pillow object
        image = Image.fromarray(image_matlike)
        result = alternative_barcode_parser(image)
    return result


def alternative_barcode_parser(image) -> str:
    """
    Uses alternative method to parse barcode from image using pyzxing
    
    Params:
        - image: filepath string or pillow image object
    """
    reader = BarCodeReader()
    result = reader.decode(image).raw
    if not result:
        raise ScannerException('Barcode Not Detected or your barcode is blank/corrupted!')
    return result
