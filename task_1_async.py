import csv
import os
import time
import aiohttp
import asyncio

import psutil
from bs4 import BeautifulSoup

URLS = ["https://dental-first.ru/catalog/",
        "https://dental-first.ru/catalog/stomatologicheskie-materialy/polirovochnye-sredstva/diadent/",
        "https://dental-first.ru/catalog/stomatologicheskoe-oborudovanie/stomatologicheskie-kresla-i-stulya/stomatologicheskie-kresla-i-stulya-castellini/"
        ]
OUTPUT_FILE = "products/products_async.csv"

async def fetch_text(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Ошибка запроса {url}: {e}")
    return None

def parse_content(html):
    if not html: return [], 0.0
    soup = BeautifulSoup(html, 'html.parser')

    cards = soup.select('div.set-card')

    results = []
    page_sum = 0.0

    for card in cards:
        try:
            title_tag = card.select_one('.set-card__title a')
            if not title_tag: continue
            name = title_tag.get_text(strip=True)

            meta_price = card.select_one('meta[itemprop="price"]')
            if meta_price:
                price_val = float(meta_price['content'])
            else:
                price_tag = card.select_one('.set-card__price')
                if price_tag:
                    clean = "".join([c for c in price_tag.get_text() if c.isdigit() or c == '.'])
                    price_val = float(clean) if clean else 0.0
                else:
                    price_val = 0.0

            results.append([name, price_val])
            page_sum += price_val
        except:
            continue

    return results, page_sum

async def worker(session, semaphore, url):
    async with semaphore:
        html = await fetch_text(session, url)
        data, total = parse_content(html)
        if data:
            print(f"Страница {url} имеет {len(data)} товаров.")
        else:
            print(f"Страница {url}: товаров нет или ошибка.")
        return data, total


async def main():
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_mem = process.memory_info().rss / 1024 / 1024

    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        print("Старт асинхронного парсинга")
        tasks = [worker(session, semaphore, url) for url in URLS]
        results = await asyncio.gather(*tasks)

    all_products = []
    total_sum = 0.0

    for data in results:
        all_products.extend(data[0])
        total_sum += data[1]

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Название товара', 'Цена'])
        writer.writerows(all_products)

    duration = time.time() - start_time
    end_mem = process.memory_info().rss / 1024 / 1024
    print(f"\n--- Итоги ---")
    print(f"Обработано страниц: {len(URLS)}")
    print(f"Всего товаров: {len(all_products)}")
    print(f"Общая сумма: {total_sum:,.2f} руб.")
    print(f"Время выполнения: {duration:.2f} сек")
    print(f"Использовано памяти: {end_mem - start_mem} МБ")

if __name__ == '__main__':
    asyncio.run(main())