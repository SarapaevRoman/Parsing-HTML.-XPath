import csv
import requests
import pandas as pd
from lxml import html
from bs4 import BeautifulSoup

# Настройки заголовков
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/131.0.0.0 Safari/537.36'}

# URL страницы
url = 'https://news.mail.ru/'
response = requests.get(url, headers=header)
links = set()

# Проверяем успешность запроса
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Поиск блока с новостями
    news_block = soup.find('div', class_="e1c482c4c8")

    if news_block is not None:
        for link in news_block.find_all('a'):
            href = link.get('href')
            if href is not None:
                links.add(href)
    else:
        print("Не удалось найти блок с новостями.")
else:
    print(f"Ошибка загрузки страницы: {response.status_code}")

# Создаем CSV-файл
with open('news_data.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Заголовок", "Ссылка", "Рубрика", "Дата", "Текст"])

    # Обходим каждую ссылку
    for link in links:
        try:
            # Переход по ссылке
            news_response = requests.get(link, headers=header)
            
            if news_response.status_code == 200:
                # Парсим страницу новости
                tree = html.fromstring(news_response.content)
                title = tree.xpath('//h1[@data-qa="Title"]/text()')
                heading = tree.xpath('//span[@data-qa="Text"]/text()')
                date = tree.xpath('//time[@datetime]/text()')
                content = tree.xpath('//div[@article-item-type]//p/text()')

                # Формируем данные
                news_data = {
                    "url": link,
                    "title": title[0] if title else "Нет заголовка",
                    "heading": heading[0] if heading else "Нет рубрики",
                    "date": date[0] if date else "Нет даты",
                    "content": " ".join(content) if content else "Нет текста"
                }

                # Записываем данные в CSV
                writer.writerow([
                    news_data["title"],
                    news_data["url"],
                    news_data["heading"],
                    news_data["date"],
                    news_data["content"]
                ])
                print(f"Новость сохранена: {news_data['title']}")
            else:
                print(f"Ошибка при загрузке новости: {news_response.status_code}")
        except Exception as e:
            print(f"Ошибка при обработке ссылки {link}: {e}")

# Чтение CSV в DataFrame
df = pd.read_csv('news_data.csv', encoding='utf-8')
print(df.head())

