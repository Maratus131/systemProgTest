import os
import time
import concurrent.futures
import asyncio

DIR_NAME = "test_files"
ALL_FILES = [os.path.join(DIR_NAME, f) for f in os.listdir(DIR_NAME) if f.endswith('.txt')]

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def run_threading():
    start = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(read_file, ALL_FILES))

    duration = time.time() - start
    print(f"[Потоки] Обработано {len(results)} файлов за {duration:.4f} сек.")


async def read_file_async(filepath):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_file, filepath)

async def run_async():
    start = time.time()

    tasks = [read_file_async(f) for f in ALL_FILES]
    results = await asyncio.gather(*tasks)

    duration = time.time() - start
    print(f"[Asyncio] Обработано {len(results)} файлов за {duration:.4f} сек.")

if __name__ == "__main__":
    print(f"Найдено файлов: {len(ALL_FILES)}")
    print("-" * 30)

    run_threading()
    asyncio.run(run_async())