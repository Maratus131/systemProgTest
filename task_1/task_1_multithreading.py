from flask import Flask, request, jsonify
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

from test_0412.task_1.parser import parse_content
from test_0412.task_1.urls import OUTPUT_FILE_THREADS
from test_0412.task_1.utils import write_to_csv

app = Flask(__name__)

all_products = []
total_sum = 0.0
lock = threading.Lock()

executor = ThreadPoolExecutor(max_workers=50)

def fetch_and_parse(url):
    response = requests.get(url, timeout=10)
    html = response.text
    return parse_content(html)

def handle_url(url):
    products, page_sum = fetch_and_parse(url)
    with lock:
        all_products.extend(products)
        global total_sum
        total_sum += page_sum
        write_to_csv(OUTPUT_FILE_THREADS, all_products)
        all_products.clear()
    return len(products), page_sum

@app.route("/parse", methods=["POST"])
def handle_request():
    data = request.get_json()
    url = data["url"]
    print(f"[THREAD SERVER] Получен URL: {url}")

    future = executor.submit(handle_url, url)
    count, page_sum = future.result()

    return jsonify({
        "count": count,
        "sum": page_sum
    })

if __name__ == "__main__":
    print("[THREAD SERVER] HTTP-многопоточный сервер запущен на 127.0.0.1:8085")
    app.run(host="127.0.0.1", port=8085, threaded=True)
