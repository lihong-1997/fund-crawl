from fund.crawl_fund import Crawl
import time
import asyncio


if __name__ == "__main__":

    startTime = time.time()
    c = Crawl()
    asyncio.run(c.run())
    endTime = time.time()
    print(f'基金数据更新完毕，耗时 {endTime - startTime:.2f}s')
