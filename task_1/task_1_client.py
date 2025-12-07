import asyncio

from test_0412.task_1.task_1_async import async_main
from test_0412.task_1.task_1_multithreading import threads_main

def run_parsers():
    asyncio.run(async_main())
    print("--------------------------")
    threads_main()

if __name__ == '__main__':
    run_parsers()