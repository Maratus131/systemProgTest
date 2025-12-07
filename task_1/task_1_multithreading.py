import csv
import os
import time
import requests
import concurrent.futures

import psutil
from bs4 import BeautifulSoup

from test_0412.task_1.parser import parse_content
from test_0412.task_1.urls import URLS, OUTPUT_FILE_THREADS
from test_0412.task_1.utils import write_to_csv


def fetch_text(url: str):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Ошибка запроса {url}: {e}")
        return None

def worker(url: str):
    html = fetch_text(url)
    data, total = parse_content(html)

    if data:
        print(f"Страница {url} имеет {len(data)} товаров.")
    else:
        print(f"Страница {url}: товаров нет или произошла ошибка.")

    return data, total


def threads_main():
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_mem = process.memory_info().rss / 1024 / 1024

    print("Старт многопоточного парсинга")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, URLS))

    all_products = []
    total_sum = 0.0

    for data, page_sum in results:
        all_products.extend(data)
        total_sum += page_sum

    write_to_csv(OUTPUT_FILE_THREADS, all_products)

    duration = time.time() - start_time
    end_mem = process.memory_info().rss / 1024 / 1024

    print("\n--- Итоги ---")
    print(f"Обработано страниц: {len(URLS)}")
    print(f"Всего товаров: {len(all_products)}")
    print(f"Общая сумма: {total_sum:,.2f} руб.")
    print(f"Время выполнения: {duration:.2f} сек")
    print(f"Использовано памяти: {end_mem - start_mem:.2f} МБ")

