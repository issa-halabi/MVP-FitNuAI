import json
import requests
from bs4 import BeautifulSoup


# extract all food names
main_page_url = "https://natureclaim.com/nutrition/"
response = requests.get(main_page_url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'id': 'nutrition'})
food_names = []

if table:
    for row in table.find_all('tr'):
        food_link = row.find('a')
        if food_link:
            food_name = food_link.text.strip()
            food_names.append(food_name)


# extract each food details
result = []
for food_name in food_names:
    print(f'extracting {food_name} page..')
    try:
        url = f"https://natureclaim.com/nutrition/info/{food_name.lower().replace(' ','-')}/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table", class_="table table-striped")

        nutrients = {'food': food_name, 'weight': 100}
        target_nutrients = {"Calories": "calories", "Total Carbs": "carbs", "Dietary Fiber": "fiber", "Protein, total": "proteins", "Total Fat": "fats"}

        # search all tables for target nutrients
        for table in tables:
            for row in table.find_all("tr")[1:]: # skip header row it causes error
                nutrient_name = row.find("td").text.strip()
                if nutrient_name in target_nutrients:
                    # add the amount of the target nutrient to the dict
                    nutrient_name = target_nutrients[nutrient_name]
                    amount_text = row.find_all("td")[1].text.strip()
                    # check if amount text is empty
                    if '-' in amount_text:
                        amount = None
                    else:
                        # remove the unit and cast to float
                        amount = float(amount_text.split()[0])
                    nutrients[nutrient_name] = amount
        result.append(nutrients)
    except Exception as e:
        print(f'error at {food_name} page: {e}')

# save result
with open('fruit_db.json', 'w') as f:
    json.dump(result, f, indent=1)
