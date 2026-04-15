import asyncio
# Day2 异步 async/await 入门 + aiohttp
'''
# 同步（Sync）：一件事做完，才能做下一件。
# 异步（Async）：一件事在等的时候，可以先去做别的事。
在异步代码中调用同步阻塞函数 asyncio.to_thread() （Python 3.9+） loop.run_in_executor()
线程安全问题
asyncio 单线程内没有竞态条件，但协程的切换点只在 await 处，因此共享变量相对安全。如果混合多线程，必须使用 asyncio.run_coroutine_threadsafe() 和线程锁。
### 决策树
是否是 CPU 密集型任务？
├─ 是 → 使用 multiprocessing（多进程）或多线程+多进程混合
│       （Python 多线程因 GIL 无法加速 CPU 任务）
└─ 否（I/O 密集型） → 看主要使用的库是否支持异步
    ├─ 是（如 aiohttp、asyncpg、aioredis） → 优先使用协程（asyncio）
    └─ 否（如 requests、pymysql、paramiko） → 使用多线程（ThreadPoolExecutor）
### 实践
协程 + 线程池：在异步主循环中，通过 asyncio.to_thread 或 loop.run_in_executor 将阻塞操作扔给线程池执行。
协程 + 多进程：CPU 密集型子任务交给 ProcessPoolExecutor，结果通过队列传回异步主线程。
例如：一个 Web 服务（FastAPI 异步处理请求）需要调用一个只支持同步的旧库（如 boto3 的某些阻塞方法），可以在异步处理函数中使用 await asyncio.to_thread(sync_func, args)。    
'''


async def task1():
    print("开始任务1")
    await asyncio.sleep(2)  # 异步等待
    print("任务1结束")

async def task2():
    print("开始任务2")
    await asyncio.sleep(5)
    print("任务2结束")

async def task(name, delay):
    print(f"Task {name} start")
    await asyncio.sleep(delay)
    print(f"Task {name} end")
    return f"Result of {name}"

# Lock：互斥锁 Event：事件通知 Condition：条件变量 Semaphore：信号量，限制并发数
async def limited_task(id):
    limit = asyncio.Semaphore(id)
    async with limit:
        print(f"Task {id} acquired semaphore")


async def main():
    # 同时运行
    # await asyncio.gather(task1(), task2())

    #  # 创建任务（立即调度，但不等待）
    t1 = asyncio.create_task(task("A", 10))
    t2 = asyncio.create_task(task("B", 1))
    # 等待所有任务完成并收集结果
    # result1 = await t1
    # result2 = await t2
    # print(result1)
    # print(result2)

    # FIRST_COMPLETED、FIRST_EXCEPTION、ALL_COMPLETED
    tasks = [asyncio.create_task(task("A", 10)), asyncio.create_task(task("B", 1))]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in done:
        print(f"Completed: {t.result()}")
    # 取消仍在运行的任务
    for p in pending:
        p.cancel()

asyncio.run(main())


