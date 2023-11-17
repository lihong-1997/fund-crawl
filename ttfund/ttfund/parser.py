"""Parse data from response"""


async def parse_strategy_id(json_response, adviser_name: str):
    data = json_response['data']
    strategy_info = data['ruleList']
    strategy_id_list = []
    for strategy in strategy_info:
        id_list = strategy['strategyId']
        strategy_id_list.extend(id_list.split('&'))
    strategy_id_list = [strategy_id.strip('*') for strategy_id in strategy_id_list]
    strategy_id_list = [ID for ID in strategy_id_list if ID != '0']
    strategy_id_list = list(set(strategy_id_list))
    adviser_strategy_id_info = {'adviser_name': adviser_name, 'tg_id_list': strategy_id_list}
    return adviser_strategy_id_info
    

async def parse_strategy_name(json_response, adviser_name: str):
    adviser_strategy_name_info = []
    for item in json_response['data'][0]['sceneList']:
        strategy_list = item['strategyList']
        for strategy in strategy_list:
            adviser_strategy_name_info.append(
                {
                    'adviser_name': adviser_name, 
                    'tg_name': strategy['name'],
                    'tg_code': strategy['code']
                })
    return adviser_strategy_name_info


async def parse_extend_info(json_response, tg_info: dict):
    is_valid = (json_response['data'] is not None)
    assert is_valid, f"<{tg_info['adviser_name']}>提供的<{tg_info['tg_name']}>策略暂无信息."
    row_name_list = ['策略名称', '机构', '策略理念', '成立来收益', '日涨幅', '风险等级', '建议持有', '成立天数', '业绩比较基准']
    row_value_list = []
    data = json_response['data']
    row_value_list.append(data['tgExtendInfo']['TGNAME'])
    row_value_list.append(data['tgExtendInfo']['LOGO_NAME'])
    info_dict = dict(data['tgExtendInfo'])
    concept1 = info_dict.get('STRATEGY_CONCEPT1')
    if concept1 is None:
        row_value_list.append(info_dict['STGCONCEPT'])
    else:
        concept_list = [concept1]
        concept2 = info_dict.get('STRATEGY_CONCEPT2')
        concept3 = info_dict.get('STRATEGY_CONCEPT3')
        if concept2 is not None:
            concept_list.append(concept2)
        if concept3 is not None:
            concept_list.append(concept3)
        tg_concept = '; '.join(concept_list)
        row_value_list.append(tg_concept)
    row_value_list.append(info_dict['SYL_LN'] + '%')
    row_value_list.append(f"{info_dict['SYRQ']}, ratio: {info_dict['SYL_D']}%")
    risk_level = {
        '1': '低风险',
        '2': '中低风险',
        '3': '中风险',
        '4': '中高风险',
        '5': '高风险'
    }
    row_value_list.append(risk_level[info_dict['RISKLEVEL']])
    recommend_hold_time = info_dict.get('RECOMMEND_HOLD_TIME')
    if recommend_hold_time is not None:
        row_value_list.append(recommend_hold_time)
    else:
        row_value_list.append('--')
    # 处理成立天数
    row_value_list.append(str(info_dict['continuedData']) + '天')
    # 处理业绩比较标准
    basic_cal_formula_remark = info_dict.get('BASIC_CAL_FORMULA_REMARK')
    if basic_cal_formula_remark is not None:
        row_value_list.append(basic_cal_formula_remark)
    else:
        row_value_list.append('--')
    # 处理特殊数据
    ch_data = {
        'user_POSITIVE_RATIO': '用户持仓正收益占比',
        'user_FGRATIO': '策略复购率',
        'user_AVGDAY': '用户平均持有时长',
        'user_STAY_RATIO': '近一年留存率',
        'excess_LN': '成立来超额收益',
        'maxretra_LN': '成立来最大回撤',
        'maxretra_1N': '近一年最大回撤',
        'mexwin_1N': '近一年跑赢基准概率',
        'profit_1Y': '持有一个月盈利概率',
        'profit_3Y': '持有三个月盈利概率',
        'profit_6Y': '持有六个月盈利概率',
        'profit_1N': '持有一年盈利概率'
    }
    tg_characteristics_page2 = dict(data['tgCharacteristics']['tgCharacteristicsPage2'])
    for key, value in tg_characteristics_page2.items():
        if key in ['user_POSITIVE_RATIO', 'user_FGRATIO', 'user_AVGDAY', 'user_STAY_RATIO']:
            if value is not None:
                row_name_list.append(ch_data[key])
                if key == 'user_AVGDAY':
                    row_value_list.append(str(value) + '天')
                else:
                    row_value_list.append(str(value) + '%')
    for key, value in tg_characteristics_page2.items():
        if key in ['excess_LN', 'maxretra_LN', 'maxretra_1N', 'mexwin_1N']:
            if value is not None:
                row_name_list.append(ch_data[key])
                row_value_list.append(str(value) + '%')
    for key, value in tg_characteristics_page2.items():
        if key in ['profit_1Y', 'profit_3Y', 'profit_6Y', 'profit_1N']:
            if value is not None:
                row_name_list.append(ch_data[key])
                row_value_list.append(str(value) + '%')

    return row_name_list, row_value_list


async def parse_netval(json_response, tg_info: dict):
    is_valid = (json_response['data'] is not None)
    assert is_valid, f"<{tg_info['adviser_name']}>提供的<{tg_info['tg_name']}>策略暂无净值数据."
    date = []
    netVal = []
    bench_netVal = []
    for item in json_response['data']:
        date.append(item['PDATE'])
        netVal.append(item['SE'] + '%')
        bench_netVal.append(item['BENCH_SE'] + '%')
    return date, netVal, bench_netVal


async def parse_warehouse(json_response, tg_info: dict):
    is_valid = ('adjustHistory' in dict(json_response['Data'])) and (json_response['Data']['adjustHistory'] is not None) and (len(json_response['Data']['adjustHistory']) > 0)
    assert is_valid, f"<{tg_info['tg_name']}>提供的<{tg_info['tg_name']}>策略暂无历史调仓数据."
    date = []
    ratio = []
    fund_type = []
    classify_fund = []
    type_map = {
        '0': '其他',
        '1': '股票型',
        '2': '货币型',
        '3': '混合型',
        '4': '其他',
        '6': '债券型',
        '7': '保本型',
        '8': '指数型',
        'a': 'QDII'}
    for item in json_response['Data']['adjustHistory']:
        adjust_list = item['adjustList']
        for i, adjust_info in enumerate(adjust_list):
            temp_dict = dict()
            fund_list = adjust_info['fundList']
            for fund in fund_list:
                temp_dict[fund['fundCode']] = fund['afterRatio'] + '%'
            date.append(item['dateStr'] if i == 0 else "")
            fund_type.append(type_map[adjust_info['type']])
            ratio.append(adjust_info['afterTotalRatio'] + '%')
            classify_fund.append(temp_dict)
    
    return date, fund_type, ratio, classify_fund
