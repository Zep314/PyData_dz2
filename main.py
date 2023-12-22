# Сбор и разметка данных (семинары)
# Урок 2. Парсинг HTML. BeautifulSoup

# Задание
# Выполнить скрейпинг данных в веб-сайта http://books.toscrape.com/ и извлечь
# информацию о всех книгах на сайте во всех категориях: название, цену, количество
# товара в наличии (In stock (19 available)) в формате integer, описание.
# Затем сохранить эту информацию в JSON-файле.

import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
from time import sleep

DELAY = 0.1

url = 'http://books.toscrape.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


def book_work(local_book):
    """
    Обработка страницы с одной книгой
    :param local_book: Кортеж (<Категория книги>, <URL страницы>)
    :return: Словарь с данными о книге из магазина
    """
    book_category, book_url = local_book[0], local_book[1]
    local_data = {'Category': book_category,  # Заполняем структуру, если поле не найдем, то структура не нарушится
                  'Name': None,
                  'UPC': None,
                  'FullPrice': None,
                  'Price': None,
                  'Tax': None,
                  'Availability': None,
                  'Amount': 0,
                  'Url': book_url,
                  'Cover': None,
                  'Rating': None,
                  }
    book_response = requests.get(book_url, headers=headers)
    page = BeautifulSoup(book_response.text, 'html.parser')
    local_data['Name'] = page.find(class_='product_main').find('h1').text
    local_data['Cover'] = "/".join(book_url.split('/')[:-1]) + '/' + page.find(class_='item active').find('img').get(
        'src')

    if page.find(class_='product_main').find(class_='star-rating One'):
        local_data['Rating'] = 1
    elif page.find(class_='product_main').find(class_='star-rating Two'):
        local_data['Rating'] = 2
    elif page.find(class_='product_main').find(class_='star-rating Three'):
        local_data['Rating'] = 3
    elif page.find(class_='product_main').find(class_='star-rating Four'):
        local_data['Rating'] = 4
    elif page.find(class_='product_main').find(class_='star-rating Five'):
        local_data['Rating'] = 5

    table = page.find(class_='table-striped')
    for row in table.find_all('tr'):
        match row.find('th').text:
            case 'UPC':
                local_data['UPC'] = row.find('td').text
            case 'Price (excl. tax)':
                try:
                    local_data['Price'] = float(re.findall(r'\d+\.\d+', row.find('td').text)[0])
                except ValueError:
                    local_data['Price'] = 0.0
            case 'Price (incl. tax)':
                try:
                    local_data['FullPrice'] = float(re.findall(r'\d+\.\d+', row.find('td').text)[0])
                except ValueError:
                    local_data['FullPrice'] = 0.0
            case 'Tax':
                try:
                    local_data['Tax'] = float(re.findall(r'\d+\.\d+', row.find('td').text)[0])
                except ValueError:
                    local_data['Tax'] = 0.0
            case 'Availability':
                local_data['Availability'] = row.find('td').text
    if local_data['Availability']:
        try:
            local_data['Amount'] = int(re.findall(r'\d+', local_data['Availability'])[0])
        except ValueError:
            local_data['Amount'] = 0
    sleep(DELAY)
    return local_data


def category_work(local_category):
    """
    Обработка одной категории
    :param local_category: Кортеж (<Категория книг>, <URL с первой страницей книг данной категории>)
    :return: Список из кортежей (<Категория>, <URL книги>) из данной категории
    """
    local_books = []
    while local_category[1]:
        category_response = requests.get(local_category[1], headers=headers)
        page = BeautifulSoup(category_response.text, 'html.parser')

        for book in page.find_all(class_='product_pod'):
            local_books.append(
                (local_category[0], "/".join(category_response.url.split('/')[:-1]) + '/' + book.find("a").get("href")))

        next_page = page.find(class_='next')  # Ищем следующую страницу
        local_category[1] = "/".join(category_response.url.split('/')[:-1]) + '/' + next_page.find('a').get('href') \
            if next_page else None  # Страницы закончились
    sleep(DELAY)
    return local_books


if __name__ == '__main__':
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    categories = [[link.text.strip(), "".join([url, '/', link.get('href')])]
                  for link in tqdm(soup.find('div', class_='side_categories').find_all('a'), '(1/3) Главная страница')
                  if link.text.strip() != 'Books']  # Эта категория содержит все книги целиком

    books = []
    for category in tqdm(categories, '(2/3) Категории'):
        books.extend(category_work(category))

    data = [book_work(book) for book in tqdm(books, '(3/3) Книги')]

    with open('rezult.json', 'w') as f:
        json.dump(data, f)

# Результат работы:
#
# C:\Work\python\Data\PyData_dz2\venv\Scripts\python.exe C:\Work\python\Data\PyData_dz2\main.py
# (1/3) Главная страница: 100%|██████████| 51/51 [00:00<?, ?it/s]
# (2/3) Категории: 100%|██████████| 50/50 [01:00<00:00,  1.22s/it]
# (3/3) Книги: 100%|██████████| 1000/1000 [10:17<00:00,  1.62it/s]
#
# Process finished with exit code 0
