# coding:utf-8
import aiohttp
import asyncio
import os
import platform
from fund.get_all_prod import get_all_prod
from fund.util import save_to_csv
from fund.parser import parse_info, parse_netval, parse_warehouse, parse_departure, parse_position


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Crawl:
    def __init__(self):
        # 存放爬取到的数据的文件名
        self.folder_name = 'DATA'
        # 获取所有策略
        self.prod_list = get_all_prod()
        self.headers = {
            'Authorization': 'OAuth2 2103100008c141676750db5e24f69c9c515e6dfc8e6a864e8',
            'dj-version': '7.20',
            'dj-sys-version': 'iOS 16.6',
            'User-Agent': 'Fund iPhone 7.20',
        }

    async def fetch_prod_info(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://fund.xueqiu.com/fundx/portfolio/ic/plan/info"
        params = {
            "ic_plan_code": prod["code"],
            "_s": "1da9e2",
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            info = await parse_info(json_response, prod["code"])

        url2 = "https://fund.xueqiu.com/fundx/portfolio/ic/plan/indicator"
        async with session.get(url2, params=params) as response:
            json_response = await response.json()
        data = json_response["data"]
        for item in data["indicator_docs"]:
            title = item["title"]
            key = list(filter(lambda k: data[k] == title, data.keys()))[0]
            key2 = key.split("_title")[0]
            info[title] = data.get(key2, None)

        os.makedirs(os.path.join(self.folder_name, prod["name"]), exist_ok=True)
        file = os.path.join(self.folder_name, prod["name"], "inform.csv")
        save_to_csv(file, info=list(info.keys()), value=list(info.values()))

    async def fetch_prod_netval(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://danjuanfunds.com/djapi/fundx/portfolio/ic/plan/growth"
        params = {
            "ic_plan_code": prod["code"],
            "period": "all",
            "type": "1"
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            date, value, bench = await parse_netval(json_response, prod["name"])
        file = os.path.join(self.folder_name, prod["name"], "netval.csv")
        save_to_csv(file, date=date, netval=value, bench=bench)

    async def fetch_prod_warehouse(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://fund.xueqiu.com/fundx/ic/strategy/adapter/strategy/adjust/history"
        params = {
            "page_no": "1",
            "page_size": "5",
            "strategy_code": prod["code"],
            "_s": "4abea8"
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
        is_valid = len(json_response["data"]["items"])
        assert is_valid, f"暂无<{prod['name']}>的调仓数据."
        adj_seq_list = [item["adjustment_no"] for item in json_response["data"]["items"]]

        all_date, all_type, all_ratio, all_fund = [], [], [], []
        url2 = "https://fund.xueqiu.com/fundx/ic/strategy/adapter/strategy/adjust/detail"
        for adj_seq in adj_seq_list:
            params = {
                "adjustment_no": adj_seq,
                "strategy_code": prod["code"],
                "_s": "54bd66",
            }
            async with session.get(url2, params=params) as response:
                json_response = await response.json()
                date_list, type_list, ratio_list, fund_list = await parse_warehouse(json_response, prod)
                all_date.extend(date_list)
                all_type.extend(type_list)
                all_ratio.extend(ratio_list)
                all_fund.extend(fund_list)

        file = os.path.join(self.folder_name, prod["name"], "warehouse.csv")
        save_to_csv(file, date=all_date, type=all_type, totalRatio=all_ratio, fund=all_fund)

    async def fetch_prod_departure(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://danjuanfunds.com/djapi/fundx/ic/activity/server/departure/scheme/list"
        params = {
            'page_no': '1',
            'page_size': '20',
            'strategy_code': prod["code"],
        }
        async with session.get(url=url, params=params) as response:
            json_response = await response.json()
        is_valid = (json_response["data"]["total_items"] != "0")
        assert is_valid, f"暂无<{prod['name']}>的发车数据."
        departure_cnt = json_response["data"]["total_items"]
        params = {
            'page_no': '1',
            'page_size': departure_cnt,
            'strategy_code': prod["code"],
        }
        async with session.get(url=url, params=params) as response:
            json_response = await response.json()
            date_list, amount_list = await parse_departure(json_response, prod)

        # 获取发车总额
        url2 = "https://danjuanfunds.com/djapi/fundx/ic/activity/server/departure/scheme/summary"
        async with session.get(url=url2, params={"strategy_code": prod["code"]}) as response:
            json_response = await response.json()
            date_list.append(" ")
            amount_list.append(json_response["data"]["departure_summary_info"]["text"])

        file = os.path.join(self.folder_name, prod["name"], "departure.csv")
        save_to_csv(file, date=date_list, amount=amount_list)

    async def fetch_prod_position(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://danjuanfunds.com/djapi/fundx/portfolio/ic/plan/v2/position/items"
        params = {
            "ic_plan_code": prod["code"],
            "request_page": "detail"
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            fund, fund_type = await parse_position(json_response, prod["name"])
        file = os.path.join(self.folder_name, prod["name"], "the_latest_warehouse.csv")
        save_to_csv(file, fund=fund, fundType=fund_type)

    async def execute_fetch_function(self, fetch_function):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            fetchers = [fetch_function(session, prod) for prod in self.prod_list]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def run(self):
        print("--------获取基本信息中--------")
        await self.execute_fetch_function(self.fetch_prod_info)
        print("--------获取净值数据中--------")
        await self.execute_fetch_function(self.fetch_prod_netval)
        print("--------获取调仓数据中--------")
        await self.execute_fetch_function(self.fetch_prod_warehouse)
        print("--------获取发车数据中--------")
        await self.execute_fetch_function(self.fetch_prod_departure)
        print("--------获取持仓数据中--------")
        await self.execute_fetch_function(self.fetch_prod_position)
