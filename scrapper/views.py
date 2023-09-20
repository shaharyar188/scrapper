from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import json
import requests


@csrf_exempt
def scrape_url(request):
    if request.method == "POST":
        try:
            product_data = []
            data = json.loads(request.body)
            url = data.get("url")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='listing__item')
            for div in divs:
                product = {}
                pro_name = div.find('h2', class_='card__address')
                if pro_name:
                    product["name"] = pro_name.get_text(strip=True)
                pro_price = div.find('p', class_='card__price')
                if pro_price:
                    price_text = pro_price.get_text(strip=True)
                    product["price"] = price_text.split('+')[0].strip()
                pro_title = div.find(
                    'p', class_='card__title--primary hide-mobile')
                if pro_title:
                    product["title"] = pro_title.get_text(strip=True)
                pro_pic = div.find('ul', class_='card__photos')
                if pro_pic:
                    img_tags = pro_pic.find_all('li')
                    product["pics"] = [img_tag.find('img').get(
                        'data-src') for img_tag in img_tags]
                pro_d = div.find('a')
                if pro_d:
                    href = pro_d.get('href')
                    product_detail = "https://www.argenprop.com" + href
                    response = requests.get(product_detail)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    pro_f = soup.find(
                        'ul', class_='property-main-features').find_all('li')
                    product_feat = [li.get_text(strip=True) for li in pro_f]
                    product["features"] = product_feat

                    pro_des_title = soup.find(
                        'p', class_='section-description--title')
                    product_des_title = pro_des_title.get_text(strip=True)
                    product["description_title"] = product_des_title
                    p_des = soup.find(
                        'div', class_='section-description--content').get_text(strip=True)
                    product_description = p_des if p_des else ""
                    product["description"] = product_description
                    location_div = soup.find(
                        'div', class_='location-container')
                    location_text = location_div.get_text(strip=True)
                    product["location"] = location_text
                    char = soup.find('ul', class_='property-features')
                    p_tags = char.find_all('p')
                    characters = [p.get_text(strip=True) for p in p_tags]
                    product["characteristics"] = characters
                product_data.append(product)
            response_data = {"product_data": product_data}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {"error": str(e)}
            return JsonResponse(response_data, status=400)
    else:
        response_data = {"error": "Invalid request method"}
        return JsonResponse(response_data, status=405)
