"""Parse data from response"""


async def parse_info(json_response, prod: dict):
    is_valid = (json_response["data"] is not None)
    assert is_valid, f"暂无<{prod['name']}>的基本数据."
    prod_type = {
        "组合": "portfolio",
        "计划": "longWin"
    }
    portfolioRiskLevelNames = {
        "1": "低风险",
        "2": "中低风险",
        "3": "中风险",
        "4": "中高风险",
        "5": "高风险"
    }
    category = {
        "0": "其它类型",
        "1": "股票型",
        "2": "债券型",
        "3": "混合型",
        "4": "货币型",
        "5": "保本型",
        "6": "指数型",
        "7": "QD",
        "8": "商品型",
        "CHINA_STOCK": "A股",
        "OVERSEA_STOCK_EMERGING": "海外新兴市场股票",
        "OIL": "原油",
        "CHINA_BOND": "境内债券",
        "OVERSEA_BOND": "海外债券",
        "GOLD": "黄金",
        "OVERSEA_STOCK_MATURE": "海外成熟市场股票",
        "CASH": "现金",
        "OTHERS": "其他"
    }
    data = json_response["data"][prod_type[prod["type"]]]
    info = {
        "策略名称": data["poName"],
        "策略提供者": f"{data['manager']['managerName']}{'(盈米基金)' if data['manager']['isYingmiExtended'] else ''}",
        "风险等级": portfolioRiskLevelNames[str(data["riskLevel"])],
        "业绩基准": data["benchmark"]["name"],
        "运行时间": f"{data['runningDays']}days",
        "组合描述": data["description"],
        "特征数据": " ".join([f"{item['displayName']}:{item['valueText']}" for item in data["featureShowcase"]]),
        "策略表现": " ".join([f"{item['displayName']}:{item['valueText']}" for item in data["performanceShowcase"]])
    }
    composition = {}
    if prod["type"] == "组合":
        fund_type = []
        ratio = []
        fund_list = []
        date = []
        for group in data["composition"]["groups"]:
            date.append(data["composition"]["updatedAt"])
            fund_type.append(category[group["categoryCode"]])
            ratio.append(group["percent"])
            temp_funds = {fund["fund"]["fundCode"]: fund["percent"] for fund in group["parts"]}
            fund_list.append(temp_funds)
        composition["0"] = date
        composition["1"] = fund_type
        composition["2"] = ratio
        composition["3"] = fund_list

    elif prod["type"] == "计划":
        composition["0"] = [category[group["categoryCode"]] for group in data["composition"]["groups"]]
        composition["1"] = [f"{str(group['unit'])}份({group['percent']})" for group in data["composition"]["groups"]]
        composition["2"] = [group["accProfitRate"] for group in data["composition"]["groups"]]

    return info, composition


async def parse_netval(json_response, prod: dict):
    prod_type = {
        "组合": "portfolio",
        "计划": "longWin"
    }
    is_valid = (len(json_response["data"][prod_type[prod["type"]]]["navHistory"]) != 0)
    assert is_valid, f"暂无<{prod['name']}>的净值数据."

    data = json_response["data"][prod_type[prod["type"]]]
    if prod["type"] == "组合":
        date = [item["date"] for item in data["navHistory"]]
        value = [str(item["value"]) for item in data["navHistory"]]
        bench = [str(item["value"]) for item in data["benchmark"]["history"]]
        return date, value, bench

    elif prod["type"] == "计划":
        date = [item["date"] for item in data["navHistory"]]
        value = [str(item["value"]) for item in data["navHistory"]]
        bench = [str(item["value"]) for item in data["benchmark"]["history"]]
        bench2 = [str(item["value"]) for item in data["comparingBenchmark"]["history"]]
        return date, value, bench, bench2


async def parse_warehouse(json_response, prod: dict):

    if prod["type"] == "组合":
        is_valid = (len(json_response["data"]["portfolio"]["adjustments"]["adjustments"]) != 0)
        assert is_valid, f"暂无<{prod['name']}>的调仓数据."
        category = {
            "0": "其它类型",
            "1": "股票型",
            "2": "债券型",
            "3": "混合型",
            "4": "货币型",
            "5": "保本型",
            "6": "指数型",
            "7": "QD",
            "8": "商品型",
            "CHINA_STOCK": "A股",
            "OVERSEA_STOCK_EMERGING": "海外新兴市场股票",
            "OIL": "原油",
            "CHINA_BOND": "境内债券",
            "OVERSEA_BOND": "海外债券",
            "GOLD": "黄金",
            "OVERSEA_STOCK_MATURE": "海外成熟市场股票",
            "CASH": "现金",
            "OTHERS": "其他"
        }
        date = []
        fund_type = []
        ratio = []
        fund_list = []
        for item in json_response["data"]["portfolio"]["adjustments"]["adjustments"]:
            for i, group in enumerate(item["groups"]):
                date.append(item["date"] if i == 0 else "")
                fund_type.append(category[group["categoryCode"]])
                ratio.append(group["afterPercent"])
                temp_funds = dict()
                for fund in group["parts"]:
                    temp_funds[fund["fund"]["fundCode"]] = fund["afterPercent"]
                fund_list.append(temp_funds)
        return date, fund_type, ratio, fund_list

    elif prod["type"] == "计划":
        is_valid = (len(json_response["composition"]) != 0)
        assert is_valid, f"暂无<{prod['name']}>的调仓数据."
        name = []
        total_ratio = []
        total_profit = []
        comp_fund = []
        for item in json_response["composition"]:
            name.append(item["className"])
            total_ratio.append(f"{item['percent']}({item['unit']}份)")
            total_profit.append(item["accProfitRate"])
            temp_dict = {}
            if not item["isCash"]:
                for fund in item["compList"]:
                    temp_dict[fund["variety"]] = {"占比": f"{fund['percent']}({fund['planUnit']}份)", "累计收益率": fund["accProfit"]}
            else:
                temp_dict["现金"] = {"占比": f"{item['percent']}({item['unit']}份)", "累计收益率": item["accProfitRate"]}
            comp_fund.append(temp_dict)

        return name, total_ratio, total_profit, comp_fund
