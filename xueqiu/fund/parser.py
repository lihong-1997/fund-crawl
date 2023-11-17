"""Parse data from response"""


async def parse_info(json_response, prod_code: str):
    is_valid = (json_response["data"] is not None)
    assert is_valid, f"暂无<{prod_code}>的基本数据."
    info = {
        "策略名称": json_response["data"]["plan_info"]["tp_plan_name"],
        "提供者": json_response["data"]["plan_info"]["tp_company_name"],
        "成立天数": json_response["data"]["plan_info"]["found_date_num"],
        "风险等级": json_response["data"]["plan_info"]["tp_risk_level_desc"],
        "起购金额": json_response["data"]["plan_info"]["trade_tip"],
        "建议持有时间": json_response["data"]["plan_desc"]["hold_time_type_desc"],
        "业绩基准": json_response["data"]["plan_info"]["benchmark_code_name"],
        json_response["data"]["plan_derived"]["yield_name"]: str(json_response["data"]["plan_derived"]["yield_since"]) + "%",
        "日涨跌": str(json_response["data"]["plan_derived"]["yield_latest"]) + "%"
    }
    return info


async def parse_netval(json_response, prod_name: str):
    is_valid = (json_response.get("data", 0))
    assert is_valid, f"暂无<{prod_name}>的净值数据."
    date = [item["date"] for item in json_response["data"]["fund_nav_growth"]]
    value = [item["value"] for item in json_response["data"]["fund_nav_growth"]]
    bench = [item["than_value"] for item in json_response["data"]["fund_nav_growth"]]
    return date, value, bench


async def parse_warehouse(json_response, prod: dict):
    date_list = []
    type_list = []
    ratio_list = []
    fund_list = []
    for i, item in enumerate(json_response["data"]["adjustment_compare"]["fund_type_compare"]["after"]):
        date_list.append(json_response["data"]["adjust_date"] if i == 0 else " ")
        type_list.append(item["name"])
        ratio_list.append(item["ratio_desc"])
        fund_type = item["type"]
        fund_detail = {}
        is_valid = (json_response["data"]["adjustment_compare"].get("fund_detail_compare", None))
        if is_valid:
            for fund in json_response["data"]["adjustment_compare"]["fund_detail_compare"]:
                if fund["fund_type"] == fund_type:
                    if json_response["data"]["show_type"] == "01":
                        fund_detail[fund["fund_code"]] = fund["ratio_after_desc"]
                    else:
                        fund_detail[fund["fund_code"]] = fund["percentage_change_desc"]
            fund_list.append(fund_detail)
        else:
            fund_list.append("暂无基金详情")
    return date_list, type_list, ratio_list, fund_list


async def parse_departure(json_response, prod: dict):
    is_valid = len(json_response["data"]["items"])
    assert is_valid, f'暂无<{prod["name"]}>的发车数据.'
    date = [item["departure_date"] for item in json_response["data"]["items"]]
    amount = [item["departure_amount"] for item in json_response["data"]["items"]]
    return date, amount


async def parse_position(json_response, prod: dict):
    is_valid = len(json_response["data"]["position_product_list"])
    assert is_valid, f'暂无<{prod["name"]}>的持仓分布数据.'
    fund_list = [{item["fund_code"]: item["percent_detail"]} for item in json_response["data"]["position_product_list"]]
    type_list = [item["fund_type_name"] for item in json_response["data"]["position_product_list"]]
    # percent_list = [item["percent_detail"] for item in json_response["data"]["position_product_list"]]
    return fund_list, type_list
