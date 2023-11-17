# coding:utf-8
import aiohttp
import pandas as pd
import asyncio
import os
import platform
from fund.get_sign import get_sign
from fund.util import save_to_csv
from fund.parser import parse_info, parse_netval, parse_warehouse


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Crawl:

    def __init__(self):
        # 获取 x_sign
        self.x_sign = get_sign()
        self.headers = {"x-sign": self.x_sign}
        # 存放爬取到的数据的文件名
        self.folder_name = 'DATA'
        # 存放组合名字的Excel文件路径
        self.path = "E:\qieman\且慢和雪球的投顾.xlsx"
        self.sheet_name = "且慢"
        self.index = 0  # 策略名称在第一列

    async def execute_fetch_prod_code(self):
        """从Excel获取全部组合的名称并获取对应的 code"""
        df = pd.read_excel(self.path, sheet_name=self.sheet_name)
        prod_name = df.iloc[0:, self.index].tolist()
        print(f"一共有{len(prod_name)}个组合待爬取")
        folders = [os.path.join(self.folder_name, name) for name in prod_name]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            fetchers = [self.fetch_prod_code(session, name) for name in prod_name]
            prods = await asyncio.gather(*fetchers)
        valid_prods = [prod for prod in prods if prod is not None]
        print(f"一共有{len(valid_prods)}个组合名称有效")
        return valid_prods

    async def fetch_prod_code(self, session: aiohttp.ClientSession, prod_name: str):
        url = "https://qieman.com/pmdj/v1/search/general"
        params = {"q": prod_name[0]}
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            results = json_response["result"]
            prod_result = results[1]
            for prod in prod_result.get("items", []):
                if prod["prodName"] == prod_name:
                    return {"name": prod_name, "code": prod["prodCode"], "type": prod["prodTypeName"]}
            print(f"Warn: <{prod_name}>未能获取code.")
            return None
            # if not prod_result["items"]:
            #     print(f"Warn: <{prod_name}>未能获取code.")
            #     return None
            # else:
            #     for prod in prod_result["items"]:
            #         if prod["prodName"] == prod_name:
            #             return {"name": prod_name, "code": prod["prodCode"], "type": prod["prodTypeName"]}
            #     print(f"Warn: <{prod_name}>未能获取code.")
            #     return None

    async def fetch_follower_cnt(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://qieman.com/alfa/v1/graphql"
        data = {
            "计划": {
                "operationName": "longWinfollowersInfo",
                "query": "query longWinfollowersInfo($poCode: String!) {\n  longWin(poCode: $poCode) {\n    buyersCount\n    followersCount\n    hasFollowed\n    __typename\n  }\n}",
                "variables": {"poCode": prod["code"]}
            },
            "组合": {
                "operationName": "followersInfo",
                "variables": {"is0009": False, "poCode": prod["code"]},
                "query": "query followersInfo($poCode: String!, $is0009: Boolean = false) {\n  portfolio(poCode: $poCode) @skip(if: $is0009) {\n    buyersCount\n    followersCount\n    hasFollowed\n    __typename\n  }\n}"
            }
        }
        async with session.post(url, json=data[prod["type"]]) as response:
            json_response = await response.json()
        if prod["type"] == "组合":
            follower_cnt = json_response["data"]["portfolio"]["followersCount"]
            buyer_cnt = json_response["data"]["portfolio"]["buyersCount"]
        elif prod["type"] == "计划":
            follower_cnt = json_response["data"]["longWin"]["followersCount"]
            buyer_cnt = json_response["data"]["longWin"]["buyersCount"]

        return follower_cnt, buyer_cnt

    async def fetch_prod_info(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://qieman.com/alfa/v1/graphql"
        prod_type = {
            "计划": {
                "operationName": "Longwin",
                "query": "query Longwin($poCode: String!) {\n  longWin(poCode: $poCode) {\n    poCode\n    poName\n    introVideo {\n      videoId\n      sourceUrl\n      coverUrl\n      url\n      commentCount\n      visitCount\n      __typename\n    }\n  benchmark {\n      name\n      __typename\n}\n    manager {\n      managerId\n      managerName\n      isVerified\n      avatarUrl\n      isYingmiExtended\n      url\n      __typename\n    }\n    runningDays\n    url\n    showNotes\n    riskLevel\n    composition {\n      groups {\n        percent\n        categoryCode\n        unit\n        accProfitRate\n        __typename\n      }\n      __typename\n    }\n    hasAdvisor\n    description\n    moneyType\n    pinnedTimelinePosts {\n      title\n      url\n      type\n      postedDate\n      __typename\n    }\n    featureShowcase {\n      valueText\n      displayName\n      fontColor\n      key\n      __typename\n    }\n    performanceShowcase {\n      key\n      displayName\n      valueText\n      fontColor\n      __typename\n    }\n    faq {\n      links {\n        text\n        link\n        __typename\n      }\n      moreButton {\n        link\n        text\n        __typename\n      }\n      __typename\n    }\n    tradeRule {\n      canBuy\n      canNotBuyReason\n      lowestBuyAmount\n      buyFeeRate\n      advisorCharge {\n        feeRate\n        mode\n        beforeFeeRate\n        __typename\n      }\n      canRedeem\n      cannotRedeemReason\n      currentTxnDate\n      buyExpectConfirmDate\n      incomeVisibleDate\n      __typename\n    }\n    latestAdjustment {\n      date\n      redeemOrders {\n        variety\n        fund {\n          fundName\n          fundCode\n          __typename\n        }\n        tradeUnit\n        __typename\n      }\n      buyOrders {\n        fund {\n          fundName\n          fundCode\n          __typename\n        }\n        variety\n        tradeUnit\n        __typename\n      }\n      __typename\n    }\n    totalUnit\n    investedUnit\n    __typename\n  }\n  preferences {\n    portfolio(poCode: $poCode) {\n      topNotice {\n        link\n        text\n        __typename\n      }\n      hasAnalysisPage\n      hasAdjustmentHistoryPage\n      hasFundInvestPoolPage\n      displayCompositionPieChart\n      displayCompositionDetailList\n      compositionDetailListSeries\n      displayMaxDrawdownOnChart\n      displayAdjustmentPoint\n      displayProfitCalculator\n      displayPerformance\n      adjustmentDetailListSeries\n      adjustmentDetailDimensions\n      displayManagerIdentity\n      displayDescriptionOnDetailPage\n      hasIntroPage\n      introImageUrls\n      displayShowcase\n      defaultComparableBenchmark\n      displayPeakPoint\n      __typename\n    }\n    __typename\n  }\n  thermometer {\n    level\n    levelDescription\n    advice(poCode: $poCode) {\n      howToBuy\n      howToSell\n      __typename\n    }\n    __typename\n  }\n  dicts {\n    portfolioCompositionCategoryNames\n    portfolioRiskLevelNames\n    __typename\n  }\n}"
            },
            "组合": {
                "operationName": "Portfolio",
                "query": "query Portfolio($poCode: String!) {\n  portfolio(poCode: $poCode) {\n    isSupportSmartAip\n    poCode\n    poName\n    introVideo {\n      videoId\n      sourceUrl\n      coverUrl\n      url\n      commentCount\n      visitCount\n      __typename\n    }\n  benchmark {\n      name\n      __typename\n}\n  manager {\n      managerId\n      managerName\n      isVerified\n      avatarUrl\n      isYingmiExtended\n      url\n      __typename\n    }\n    runningDays\n    url\n    showNotes\n    riskLevel\n    composition {\n      updatedAt\n      groups {\n        parts {\n          percent\n          categoryCode\n          fund {\n            fundCode\n            fundName\n            nav\n            navDate\n            dailyReturn\n            __typename\n          }\n          candidateFund {\n            fundCode\n            fundName\n            __typename\n          }\n          candidateReason\n          latestMovementName\n          latestMovement\n          varietyName\n          __typename\n        }\n        percent\n        categoryCode\n        __typename\n      }\n      __typename\n    }\n    hasAdvisor\n    description\n    moneyType\n    pinnedTimelinePosts {\n      title\n      url\n      type\n      postedDate\n      __typename\n    }\n    featureShowcase {\n      valueText\n      displayName\n      fontColor\n      key\n      __typename\n    }\n    performanceShowcase {\n      key\n      displayName\n      valueText\n      fontColor\n      __typename\n    }\n    faq {\n      links {\n        text\n        link\n        __typename\n      }\n      moreButton {\n        link\n        text\n        __typename\n      }\n      __typename\n    }\n    latestSignal {\n      date\n      shortDescription\n      __typename\n    }\n    runningWithRealMoney\n    tradeRule {\n      canBuy\n      canNotBuyReason\n      lowestBuyAmount\n      buyFeeRate\n      advisorCharge {\n        feeRate\n        mode\n        beforeFeeRate\n        description\n        stepRates {\n          description\n          __typename\n        }\n        __typename\n      }\n      canRedeem\n      cannotRedeemReason\n      currentTxnDate\n      buyExpectConfirmDate\n      incomeVisibleDate\n      __typename\n    }\n    __typename\n  }\n  preferences {\n    portfolio(poCode: $poCode) {\n      topNotice {\n        link\n        text\n        __typename\n      }\n      hasAnalysisPage\n      hasAdjustmentHistoryPage\n      hasFundInvestPoolPage\n      displayCompositionPieChart\n      displayCompositionDetailList\n      compositionDetailListSeries\n      displayMaxDrawdownOnChart\n      displayAdjustmentPoint\n      displayProfitCalculator\n      displayPerformance\n      adjustmentDetailListSeries\n      adjustmentDetailDimensions\n      displayManagerIdentity\n      displayDescriptionOnDetailPage\n      hasIntroPage\n      introImageUrls\n      displayShowcase\n      defaultComparableBenchmark\n      displayPeakPoint\n      __typename\n    }\n    __typename\n  }\n  thermometer {\n    level\n    levelDescription\n    advice(poCode: $poCode) {\n      howToBuy\n      howToSell\n      __typename\n    }\n    __typename\n  }\n  dicts {\n    portfolioCompositionCategoryNames\n    portfolioRiskLevelNames\n    __typename\n  }\n}"
            }
        }
        data = {
            "operationName": prod_type[prod["type"]]["operationName"],
            "variables": {
                "poCode": prod["code"]
            },
            "query": prod_type[prod["type"]]["query"]
        }
        async with session.post(url, json=data) as response:
            json_response = await response.json()
            prod_info, com_info = await parse_info(json_response, prod)

            follower_cnt, buyer_cnt = await self.fetch_follower_cnt(session, prod)
            prod_info["关注数"] = follower_cnt
            prod_info["跟投数"] = buyer_cnt
            
            file = os.path.join(self.folder_name, prod["name"], "inform.csv")
            save_to_csv(file, info=list(prod_info.keys()), value=list(prod_info.values()))

            file2 = os.path.join(self.folder_name, prod["name"], "the_latest_warehouse.csv")
            if prod["type"] == "组合":
                save_to_csv(file2,
                            date=com_info["0"],
                            type=com_info["1"],
                            totalratio=com_info["2"],
                            fundlist=com_info["3"])
            elif prod["type"] == "计划":
                save_to_csv(file2,
                            资产=com_info["0"],
                            份数=com_info["1"],
                            累计收益率=com_info["2"])
            else:
                print(f"Warn: <{prod['name']}>不属于已知的类型.")

    async def execute_fetch_prod_info(self, prods: list):
        """获取组合的基本信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            fetchers = [self.fetch_prod_info(session, prod) for prod in prods]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def fetch_prod_netval(self, session: aiohttp.ClientSession, prod: dict):
        url = "https://qieman.com/alfa/v1/graphql"
        prod_type = {
            "计划": {
                "operationName": "LongWinNavHistory",
                "query": "query LongWinNavHistory($poCode: String!, $hasAdjustment: Boolean!, $range: ChartRange, $comparingIndexCode: String, $hasComparingIndex: Boolean!, $indexCode: String!, $isSInvested: Boolean = false) {\n  longWin(poCode: $poCode) {\n    navHistory(range: $range) @skip(if: $isSInvested) {\n      date\n      value\n      extra\n      __typename\n    }\n    investedNavHistory(range: $range) @include(if: $isSInvested) {\n      date\n      value\n      extra\n      __typename\n    }\n    benchmark(indexCode: $indexCode) {\n      name\n      indexCode\n      indexShortName\n      description\n      history(range: $range) {\n        date\n        value\n        __typename\n      }\n      __typename\n    }\n    adjustments @include(if: $hasAdjustment) {\n      date\n      __typename\n    }\n    comparableBenchmarks {\n      description\n      indexCode\n      indexShortName\n      name\n      __typename\n    }\n    comparingBenchmark: benchmark(indexCode: $comparingIndexCode) @include(if: $hasComparingIndex) {\n      description\n      indexCode\n      name\n      history(range: $range) {\n        date\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
                "variables": {
                    "comparingIndexCode": "csi500",
                    "hasAdjustment": False,
                    "hasComparingIndex": True,
                    "indexCode": "hs300", # TODO:
                    "isSInvested": False,
                    "poCode": prod["code"],
                    "range": {
                        "period": "Max"
                    }
                }
            },
            "组合": {
                "operationName": "NavHistory",
                "query": "query NavHistory($poCode: String!, $hasExpeData: Boolean!, $hasAdjustment: Boolean!, $all: Boolean, $range: ChartRange, $comparingIndexCode: String, $hasComparingIndex: Boolean!) {\n  portfolio(poCode: $poCode) {\n    navHistory(range: $range) {\n      date\n      value\n      __typename\n    }\n    expectedNavHistory(range: $range) @include(if: $hasExpeData) {\n      date\n      extra\n      __typename\n    }\n    benchmark {\n      name\n      description\n      history(range: $range) {\n        date\n        value\n        __typename\n      }\n      __typename\n    }\n    adjustments(all: $all) @include(if: $hasAdjustment) {\n      adjustments {\n        date\n        __typename\n      }\n      __typename\n    }\n    signals(all: $all) @include(if: $hasAdjustment) {\n      signals {\n        date\n        __typename\n      }\n      __typename\n    }\n    comparableBenchmarks {\n      description\n      indexCode\n      indexShortName\n      name\n      __typename\n    }\n    comparingBenchmark: benchmark(indexCode: $comparingIndexCode) @include(if: $hasComparingIndex) {\n      description\n      indexCode\n      name\n      history(range: $range) {\n        date\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
                "variables": {
                    "poCode": prod["code"],
                    "comparingIndexCode": "",
                    "hasComparingIndex": False,
                    "hasExpeData": False,
                    "hasAdjustment": True,
                    "all": True,
                    "range": {
                        "period": "Max"
                    }
                }
            }
        }
        data = {
            "operationName": prod_type[prod["type"]]["operationName"],
            "variables": prod_type[prod["type"]]["variables"],
            "query": prod_type[prod["type"]]["query"]
        }
        file = os.path.join(self.folder_name, prod["name"], "netval.csv")
        async with session.post(url, json=data) as response:
            json_response = await response.json()
            if prod["type"] == "组合":
                date, value, bench = await parse_netval(json_response, prod)
                save_to_csv(file, date=date, value=value, bench=bench)
            elif prod["type"] == "计划":
                date, value, bench, bench2 = await parse_netval(json_response, prod)
                save_to_csv(file, date=date, value=value, bench=bench, csi500=bench2)
            else:
                print(f"Warn: <{prod['name']}>不属于已知的类型.")

    async def execute_fetch_prod_netval(self, prods: list):
        """获取组合的净值信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            fetchers = [self.fetch_prod_netval(session, prod) for prod in prods]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def fetch_prod_warehouse(self, session: aiohttp.ClientSession, prod: dict):
        if prod["type"] == "组合":
            url = "https://qieman.com/alfa/v1/graphql"
            page_data = {
                "operationName": "Adjustment",
                "variables": {
                    "poCode": prod["code"],
                    "page": {
                        "size": 15
                    },
                    "needPreference": False,
                    "needCategoryDict": False
                },
                "query": "query Adjustment($poCode: String!, $page: Pagination, $needPreference: Boolean!, $needCategoryDict: Boolean!) {\n  portfolio(poCode: $poCode) {\n    isSupportSmartAip\n    adjustments(page: $page) {\n      adjustments {\n        date\n        comment\n        adjustmentId\n        groups {\n          categoryCode\n          movementName\n          parts {\n            fund {\n              fundCode\n              fundName\n              __typename\n            }\n            movementName\n            beforePercent\n            afterPercent\n            categoryCode\n            __typename\n          }\n          beforePercent\n          afterPercent\n          __typename\n        }\n        __typename\n      }\n      totalCount\n      pageInfo {\n        hasMore\n        cursor\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  preferences @include(if: $needPreference) {\n    portfolio(poCode: $poCode) {\n      adjustmentDetailListSeries\n      adjustmentDetailDimensions\n      __typename\n    }\n    __typename\n  }\n  dicts @include(if: $needCategoryDict) {\n    portfolioCompositionCategoryNames\n    portfolioRiskLevelNames\n    __typename\n  }\n}"
            }
            async with session.post(url=url, json=page_data) as response:
                json_response = await response.json()
                page_num = json_response["data"]["portfolio"]["adjustments"]["totalCount"]
            if page_num is None:
                # 查看是否有历史发车数据
                url2 = f'https://qieman.com/pmdj/v1/pomodels/{str(prod["code"])}/sig-adjustments'
                params = {
                  "page": 0,
                  "size": 1
                }
                async with session.get(url=url2, params=params) as response:
                    json_response = await response.json()
                    data_num = json_response["totalElements"]
                if data_num is None:
                    print(f"暂无<{prod['name']}>的调仓数据.")
                else:
                    params = {
                        "page": 0,
                        "size": json_response["totalElements"]
                    }
                    async with session.get(url=url2, params=params) as response:
                        json_response = await response.json()
                    adjust_datas = json_response["content"]
                    date = [item["adjustedDate"] for item in adjust_datas]
                    suggest = [item["sigSummary"] for item in adjust_datas]
                    fund_list, total_amount_list = [], []
                    for item in adjust_datas:
                        fund = {f["fundCode"]: f["percent"] for f in item['buyOrders']}
                        total_amount = item.get("buyTotalAmount")
                        if total_amount is None:
                            total_amount = sum(f["amount"] for f in item['buyOrders'])
                        fund_list.append(fund)
                        total_amount_list.append(f"{str(total_amount)} 元")

                    file = os.path.join(self.folder_name, prod["name"], "warehouse2.csv")
                    save_to_csv(file, 发车日期=date, 发车建议=suggest, 总金额=total_amount_list, 基金列表=fund_list)

            else:
                data = {
                    "operationName": "Adjustment",
                    "variables": {
                        "poCode": prod["code"],
                        "page": {
                            "size": page_num
                        },
                        "needPreference": True,
                        "needCategoryDict": True
                    },
                    "query": "query Adjustment($poCode: String!, $page: Pagination, $needPreference: Boolean!, $needCategoryDict: Boolean!) {\n  portfolio(poCode: $poCode) {\n    isSupportSmartAip\n    adjustments(page: $page) {\n      adjustments {\n        date\n        comment\n        adjustmentId\n        groups {\n          categoryCode\n          movementName\n          parts {\n            fund {\n              fundCode\n              fundName\n              __typename\n            }\n            movementName\n            beforePercent\n            afterPercent\n            categoryCode\n            __typename\n          }\n          beforePercent\n          afterPercent\n          __typename\n        }\n        __typename\n      }\n      totalCount\n      pageInfo {\n        hasMore\n        cursor\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  preferences @include(if: $needPreference) {\n    portfolio(poCode: $poCode) {\n      adjustmentDetailListSeries\n      adjustmentDetailDimensions\n      __typename\n    }\n    __typename\n  }\n  dicts @include(if: $needCategoryDict) {\n    portfolioCompositionCategoryNames\n    portfolioRiskLevelNames\n    __typename\n  }\n}"
                }
                async with session.post(url, json=data) as response:
                    json_response = await response.json()
                    date, fund_type, total_ratio, fund_list = await parse_warehouse(json_response, prod)
                    file = os.path.join(self.folder_name, prod["name"], "warehouse.csv")
                    save_to_csv(file, date=date, type=fund_type, totalratio=total_ratio, fundlist=fund_list)

        elif prod["type"] == "计划":
            url = "https://qieman.com/pmdj/v2/long-win/plan"
            params = {
                "prodCode": prod["code"]
            }
            async with session.get(url, params=params) as response:
                json_response = await response.json()
                name, total_ratio, total_profit, comp_fund = await parse_warehouse(json_response, prod)
                file = os.path.join(self.folder_name, prod["name"], "warehouse.csv")
                save_to_csv(file, name=name, totalRatio=total_ratio, totalProfit=total_profit, fundList=comp_fund)
        else:
            print(f"Warn: <{prod['name']}>不属于已知的类型.")

    async def execute_fetch_prod_warehouse(self, prods: list):
        """获取组合的调仓记录"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            fetchers = [self.fetch_prod_warehouse(session, prod) for prod in prods]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def run(self):
        prods = await self.execute_fetch_prod_code()
        await self.execute_fetch_prod_info(prods)
        print("------获取净值数据中------")
        await self.execute_fetch_prod_netval(prods)
        print("------获取调仓记录\历史发车中------")
        await self.execute_fetch_prod_warehouse(prods)
