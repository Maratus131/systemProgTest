import asyncio

import aiohttp
from aiohttp import web

from task1_async import parse_content
from test_0412.task_1.urls import OUTPUT_FILE_ASYNC
from test_0412.task_1.utils import write_to_csv_async

all_products = []
total_sum = 0.0
lock = asyncio.Lock()

async def handle_request(req):
    global all_products, total_sum

    data = await req.json()
    url = data["url"]
    print(f"[ASYNC SERVER] Получен URL: {url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    products, page_sum = parse_content(html)

    async with lock:
        all_products.extend(products)
        total_sum += page_sum
        await write_to_csv_async(OUTPUT_FILE_ASYNC, all_products)
        all_products.clear()

    return web.json_response({
        "count": len(products),
        "sum": page_sum
    })

app = web.Application()
app.router.add_post("/parse", handle_request)

def start_server():
    web.run_app(app, host="127.0.0.1", port=8081)

if __name__ == "__main__":
    start_server()

