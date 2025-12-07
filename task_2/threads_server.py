from flask import Flask, request, jsonify
import threading
import concurrent.futures
import os

app = Flask(__name__)

total_lines = 0
processed_files = 0
lock = threading.Lock()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1000)

def count_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

@app.route("/count", methods=["POST"])
def handle_request():
    global total_lines, processed_files

    data = request.get_json()
    filepath = data["filepath"]

    print(f"[THREAD SERVER] Получен файл: {filepath}")

    future = executor.submit(count_lines, filepath)
    line_count = future.result()

    with lock:
        total_lines += line_count
        processed_files += 1

    return jsonify({
        "file": filepath,
        "lines": line_count
    })

if __name__ == "__main__":
    print("[THREAD SERVER] Запущен на 127.0.0.1:8090")
    app.run(host="127.0.0.1", port=8090, threaded=True)
