import requests
import json
from bs4 import BeautifulSoup
import pandas as pd



INITIAL_URL = 'https://www.50pros.com/top-50/top-50-advertising-firms-hire-an-advertising-agency'


def get_all_url_endpoints() -> list:
    response = requests.get(url=INITIAL_URL)
    response.raise_for_status()
    soup = BeautifulSoup(markup=response.text, features='lxml')
    url_tags_list = soup.select(selector='.category-block')
    urls_list = [{'url': tag['href'], 'name': tag.find(class_='category-text').text} for tag in url_tags_list][1:]
    print(f"number of categories on the site: {len(urls_list)}")
    return urls_list


def scrape_category(url: str):
    category_response = requests.get(url=url)
    category_response.raise_for_status()
    soup = BeautifulSoup(markup=category_response.text, features='lxml')
    card_divs_list = soup.select(selector='.link-block-7')
    companies = []
    for card in card_divs_list:
        tag_3_tags = card.find_all(class_="tag-3")
        tags_3 = [tag.text for tag in tag_3_tags if tag.text]
        footer_tags = card.find_all(class_="text-block-85")
        companies.append({
            'name': card.find(class_="tool-name").text,
            'url': card['href'],
            'location': card.find(class_="tag-2").text,
            'tags_3': tags_3,
            'description': card.find(class_="text-block-84").text,
            'date': footer_tags[0].text,
            'people': footer_tags[1].text,
            'stars': footer_tags[2].text

        })
    return companies


def save_raw_json():
    result = []
    categories = get_all_url_endpoints()
    n = len(categories)
    i = 1
    for category in categories:
        companies = scrape_category(url=category['url'])
        result.append({category['name']: companies})
        print(f"{i} of {n}. Category: {category['name']}. {len(companies)} companies scraped.")
        i += 1
    with open(file='raw_data.json', mode='w') as f:
        json.dump(obj=result, fp=f, indent=2)
    print("Raw data saved")


def json_to_df():
    with open(file='raw_data.json', mode='r') as f:
        data_json = json.load(f)
    formatted_data = {
        'category': [],
        'company_name': [],
        'website': [],
        'location': [],
        'tags': [],
        'description': [],
        'year': [],
        'staff': [],
        'stars': []
    }
    for category in data_json:
        category_name = list(category.keys())[0]
        for company in category[category_name]:
            formatted_data['category'].append(category_name)
            formatted_data['company_name'].append(company['name'])
            formatted_data['website'].append(company['url'])
            formatted_data['location'].append(company['location'])
            formatted_data['tags'].append(', '.join(company['tags_3']))
            formatted_data['description'].append(company['description'])
            formatted_data['year'].append(company['date'])
            formatted_data['staff'].append(company['people'])
            formatted_data['stars'].append(company['stars'])
    return pd.DataFrame(data=formatted_data)


def main():
    save_raw_json()
    df = json_to_df()
    df.to_excel(excel_writer='all_companies.xlsx', index=False)


if __name__ == '__main__':
    main()
