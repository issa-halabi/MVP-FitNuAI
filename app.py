import gradio as gr
from utils.model import GPT_DishAnalyzer
from utils.db_manager import retrieve_corresponding_calories, get_unique_dishes, get_data_for_gpt


def analyze_image(image_file_path: str, weight: float) -> tuple:
    """
    Use the dish analyzer object to analyze a given image and update gradio's components accordingly.
    Returns: (tuple) of food_type (str) & number of calories (str)
    """
    food_type = model.predict(image_file_path)
    calories = retrieve_corresponding_calories(food_type, weight, data)
    return food_type, calories


# read the header code from the html file
with open('./templates/header.html', 'r') as file:
    html_header = file.read()

with gr.Blocks(theme=gr.themes.Soft(), css='./templates/styling.css') as app:
    gr.HTML(html_header)
    with gr.Row():
        # input part
        with gr.Column():
            image_input = gr.Image(sources=['upload', 'clipboard'], type='filepath')
            gr.Markdown('Please upload a clear image of a single dish, with minimal background and no obstacles. This will help our model accurately identify the food.')
            weight = gr.Number(value=100, label='Optional: Food weight (in grams)', minimum=1, step=5)
            submit_button = gr.Button('Submit Image')
        # output part
        with gr.Column():
            gr.Markdown('## Result')
            classification_output = gr.Textbox(label='Food Type', interactive=False)
            calories_output = gr.Textbox(label='Estimated Calories (per unit)', interactive=False)
        submit_button.click(fn=analyze_image, inputs=[image_input, weight], outputs=[classification_output, calories_output])


if __name__ == '__main__':
    data = get_data_for_gpt()
    labels = get_unique_dishes(data)
    model = GPT_DishAnalyzer(labels)
    app.launch(share=False)
