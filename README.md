# MVP-Fitness-AI
This application provides endpoints to retrieve nutrifacts for food. It support food names, food images, and products barcodes.

## Endpoints:
**1. Get nutrition facts by food name:**
- Endpoint path: "/food_name/{food_name}"
- Method: GET
- Parameters: food_name string passed as path parameter
- Responses (with custom message):
    - 200 OK: returns the nutritional information of all the dishes that contain the given query in their name, along with their images
    - 404 Not Found:
        - food_name not found in database
- Example Request:
```
GET /food_name/apple
```

Example Response:
```
{
    "search_results":[
        {
            "food":"batata mahchi",
            "weight":100,
            "calories":279,
            "carbs":70,
            "fat":0,
            "protein":0,
            "fiber":0,
            "image":""
        },
        {
            "food":"banana",
            "weight":100,
            "calories":279,
            "carbs":70,
            "fat":0,
            "protein":0,
            "fiber":0,
            "image":""
        }
    ]
}
```


**2. Get nutrition facts by food image:**
- Endpoint path: "/food_image/"
- Method: POST
- Request Body:
    - image_base64 string, base64-encoded image of a single type of food
- Responses:
    - 200 OK: returns the nutritional information of the foods recognized in the given image along with their images
    - 404 Not Found:
        - Unknown or Unrecognized food
- Example Request:
```
{
    image_base64: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAk..."
}
```

Example Response:
```
[
    {
        "food":"apple",
        "weight":100,
        "calories":279,
        "carbs":70,
        "fat":0,
        "protein":0,
        "fiber":0,
        "image":""
    },
    {
        "food":"banana",
        "weight":100,
        ...
    },
    ...
]
```

**3. Get nutrition facts by barcode:**
- Endpoint path: "/barcode/{code}"
- Method: GET
- Parameters: code string passed as path parameter
- Responses:
    - 200 OK: Returns the nutritional information of the product with the given barcode along with its image.
    - 404 Not Found:
        - Product not found in database.
- Example Request:
```
GET /barcode/123456789012
```

Example Response:
```
{
    "food":"jelly",
    "weight":100,
    "calories":279,
    "carbs":70,
    "fat":0,
    "protein":0,
    "fiber":0,
    "image": ""
}
```

## Components:

### Model:
This module offers end-to-end DishAnalyzer class that recognizes food type in a given dish image.
It is used for the food_image endpoint.

The DishAnalyzer class consists of 3 main methods:
- **encode_input:**: Encodes the image at the given filepath into model-suitable input.
- **decode_output:** Decodes the prediction from the model into understandable format
- **predict:** Uses the finetuned model (from Finetuning part) to predict the type of food & number of calories in the given image, utilizing the 2 methods above, plus db_manager.


### db_manager:
This module is responsible for retrieving calories for each food type from the database (which is currently simply a json file). It includes 5 methods:
- **get_data_for_gpt:** Returns dataframe read from [arabic_food_db.json](./DB/arabic_food_db.json) & [fruit_db](./DB/fruit_db.json) files
- **get_all_data:** Return dataframe from all data files in [/DB](./DB/)
- **get_unique_dishes:** Returns a list of unique dishes from the database
- **get_food_info:** Retrieves all information saved in the database about the given food type
- **retrieve_corresponding_calories:** Retrieves the calories of a given food_type (uses get_food_info). It takes into account given weight of the food.

### barcode_scanner:
This module provides methods needed for the barcode_image endpoint, which enables retrieving the nutrufacts of a food product through an image of its barcode.

It includes 4 methods:
- **get_nutrition_facts:** Get nutrition facts for a given code.
- **parse_barcode_image:** Parse a barcode image and return the barcode value.
- **parse_barcode_image_path:** Parse a barcode image from a file path and return the barcode value.
- **parse_barcode_image_base64:** Parse a barcode image from a base64 string and return the barcode value.


### App (Gradio interface for testing):
This is the interface, the web app part of the project. It is a basic input-output display:
- Input: Dish Image & Food Weight
- Output: predicted food type & number of calories, with a confidence score in the prediction

It uses 2 additional files, for html & css


## Usage (docker)
Install & Use git LFS
```
brew install git-lfs

git lfs install

git lfs fetch

git lfs checkout
```

Install necessary libraries
```
pip install -r requirements.txt
```

Create .env file, and write inside it your OPENAI_APIKEY there:
```
OPENAI_API_KEY="your_api_key"
```

Build & Run the docker image
```
docker-compose --env-file .env up --build
```

Test the API through the endpoints, at http://localhost:8000/docs
