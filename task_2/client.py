import asyncio
import time
import aiohttp
import requests
import psutil
import os

DIR_NAME = "test_files"
FILES = [os.path.join(DIR_NAME, f) for f in os.listdir(DIR_NAME) if f.endswith(".txt")]

ASYNC_URL = "http://127.0.0.1:8091/count"
THREAD_URL = "http://127.0.0.1:8090/count"


def get_benchmark(fn):
    process = psutil.Process()
    ram_before = process.memory_info().rss
    cpu_before = psutil.cpu_percent(interval=None)

    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start

    ram_after = process.memory_info().rss
    cpu_after = psutil.cpu_percent(interval=None)

    return {
        "result": result,
        "time": elapsed,
        "ram": ram_after - ram_before,
        "cpu": cpu_after - cpu_before
    }


async def async_request(session, filepath):
    async with session.post(ASYNC_URL, json={"filepath": filepath}) as resp:
        return await resp.json()


async def run_async_client():
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(async_request(session, f)) for f in FILES]
        return await asyncio.gather(*tasks)


def async_client():
    return asyncio.run(run_async_client())


def thread_request(filepath):
    resp = requests.post(THREAD_URL, json={"filepath": filepath})
    return resp.json()

def run_thread_client():
    return [thread_request(f) for f in FILES]


if __name__ == "__main__":
    print(f"Тестирование серверов, файлов найдено: {len(FILES)}")

    async_metrics = get_benchmark(async_client)
    thread_metrics = get_benchmark(run_thread_client)

    print("\nСРАВНЕНИЕ")
    print(f"Время async:  {async_metrics['time']:.3f} сек")
    print(f"Время thread: {thread_metrics['time']:.3f} сек")
    print()
    print(f"RAM async:  {async_metrics['ram'] / 1024 / 1024:.2f} МБ")
    print(f"RAM thread: {thread_metrics['ram'] / 1024 / 1024:.2f} МБ")

    print(f"CPU async:  {async_metrics['cpu']} %")
    print(f"CPU thread: {thread_metrics['cpu']} %\n")

    print()
    print("------ РЕЗУЛЬТАТЫ --------")
    print("Ответы async-сервера:", async_metrics["result"])
    print("Ответы thread-сервера:", thread_metrics["result"])
