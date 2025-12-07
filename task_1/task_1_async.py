import asyncio
import os
import time

import aiohttp
import psutil

from test_0412.task_1.parser import parse_content
from test_0412.task_1.urls import URLS, OUTPUT_FILE_ASYNC
from test_0412.task_1.utils import write_to_csv

async def fetch_text(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Ошибка запроса {url}: {e}")
    return None

async def worker(session, semaphore, url):
    async with semaphore:
        html = await fetch_text(session, url)
        data, total = parse_content(html)
        if data:
            print(f"Страница {url} имеет {len(data)} товаров.")
        else:
            print(f"Страница {url}: товаров нет или ошибка.")
        return data, total


async def async_main():
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

    write_to_csv(OUTPUT_FILE_ASYNC, all_products)

    duration = time.time() - start_time
    end_mem = process.memory_info().rss / 1024 / 1024
    print(f"\n--- Итоги ---")
    print(f"Обработано страниц: {len(URLS)}")
    print(f"Всего товаров: {len(all_products)}")
    print(f"Общая сумма: {total_sum:,.2f} руб.")
    print(f"Время выполнения: {duration:.2f} сек")
    print(f"Использовано памяти: {end_mem - start_mem} МБ")