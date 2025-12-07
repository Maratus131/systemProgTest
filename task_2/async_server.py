import asyncio
from aiohttp import web

total_lines = 0
processed_files = 0
lock = asyncio.Lock()

def count_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

async def handle_request(req):
    global total_lines, processed_files

    data = await req.json()
    filepath = data["filepath"]

    print(f"[ASYNC SERVER] Получен файл: {filepath}")

    loop = asyncio.get_running_loop()
    line_count = await loop.run_in_executor(None, count_lines, filepath)

    async with lock:
        total_lines += line_count
        processed_files += 1

    return web.json_response({
        "file": filepath,
        "lines": line_count
    })

app = web.Application()
app.router.add_post("/count", handle_request)

def start_server():
    print("[ASYNC SERVER] Запущен на 127.0.0.1:8091")
    web.run_app(app, host="127.0.0.1", port=8091)

if __name__ == "__main__":
    start_server()
