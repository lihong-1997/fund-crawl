# coding:utf-8
import aiohttp
from ttfund.get_token import GetToken
from ttfund.util import save_to_csv
from ttfund.parser import parse_extend_info, parse_strategy_id, parse_strategy_name, parse_netval, parse_warehouse
import requests
import asyncio
import os
import platform


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Crawl(GetToken):

    def __init__(self):
        super().__init__()
        # 存放爬取到的数据的文件名
        self.folder_name = 'DATA'
        # self.error_tgs = []

    def get_advisers_info(self) -> list:
        """获取全部投顾公司的信息"""
        url = 'https://appactive.1234567.com.cn/AppoperationApi/Modules/GetAdvicerHome'
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://mpservice.com/b0381a3b634440379d330b69f09d3f8e/release/pages/selectStrategy/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        params = {
            'AppVersion': self.app_version,
            'DeviceId': self.device_id,
            'PlatId': '1',
            'UserId': self.user_id,
            'passportid': self.passport_id,
            'product': 'EFund'
        }
        try:
            response = requests.get(url=url, headers=headers, params=params, timeout=self.timeout)
        except Exception as e:
            print('Error occurs while getting adviser code, ', e)
        else:
            json_response = response.json()
            for module in json_response['datas']['Modules']:
                if module['Title'] == '持牌投顾':
                    return module['CustomArray']
            print('未找到持牌投顾')
            return []

    async def get_strategy_id(self, session: aiohttp.ClientSession, adviser: dict):
        """获取单个投顾公司提供的所有策略的ID"""
        url = 'https://universalapi.1234567.com.cn/hxfundtrade/auxiliary/kycQuestionV2'
        params = {
            'AppType': 'ttjj',
            'MobileKey': self.device_id,
            'ctoken': self.ctoken,
            'partner': adviser['AdvicerCode'],
            'plat': 'Iphone',
            'serverversion': self.app_version,
            'userId': self.user_id,
            'utoken': self.utoken,
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            adviser_strategy_id_info = await parse_strategy_id(json_response, adviser['AdvicerName'])
            return adviser_strategy_id_info
    
    async def get_strategy_name(self, session: aiohttp.ClientSession, tg_id_info: dict):
        """获取单个投顾公司提供的所有策略的名字"""
        code_list = ','.join(tg_id_info['tg_id_list'])
        url = 'https://uni-fundts.1234567.com.cn/combine/investAdviserAggr/tgStgSceneAggrByCodeList'
        params = {
            'codeList': code_list,
            'ctoken': self.ctoken,
            'appVersion': self.app_version,
            'deviceid': self.device_id,
            'passportctoken': self.passport_ctoken,
            'passportid': self.passport_id,
            'passportutoken': self.passport_utoken,
            'plat': 'Iphone',
            'product': 'Fund',
            'serverversion': self.app_version,
            'userid': self.user_id,
            'utoken': self.utoken,
            'version': self.app_version
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            adviser_strategy_name_info = await parse_strategy_name(json_response, tg_id_info['adviser_name'])
            return adviser_strategy_name_info

    async def get_all_strategies(self, advisers: list):
        """整合所有投顾公司的全部策略, 每个策略包含:发行机构名字,策略ID,策略名字"""
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://mpservice.com/funda91a99886abf7e/release/pages/question/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            fetchers = [self.get_strategy_id(session, adviser) for adviser in advisers]
            all_adviser_strategy_id_info = await asyncio.gather(*fetchers)
       
        all_adviser_strategy_info = []
        async with aiohttp.ClientSession(headers=headers) as session:
            fetchers = [self.get_strategy_name(session, adviser_strategy_id_info) 
                        for adviser_strategy_id_info in all_adviser_strategy_id_info]
            for finished_task in asyncio.as_completed(fetchers):
                adviser_strategy_name_info = await finished_task
                for item in adviser_strategy_name_info:
                    folder = os.path.join(self.folder_name, item['adviser_name'], item['tg_name'])
                    os.makedirs(folder, exist_ok=True)
                all_adviser_strategy_info.extend(adviser_strategy_name_info)

        print(f'一共有 {len(all_adviser_strategy_info)} 条策略')
        return all_adviser_strategy_info

    async def execute_fetch_extend_info(self, tg_list: list):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://mpservice.com/funda91a99886abf7e/release/pages/strategyDetail/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            fetchers = [self.fetch_and_save_extend_info(session, tg) for tg in tg_list]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def execute_fetch_netval(self, tg_list: list):
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://mpservice.com/funda91a99886abf7e/release/pages/strategyDetail/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            fetchers = [self.fetch_and_save_netval(session, tg) for tg in tg_list]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def execute_fetch_warehouse(self, tg_list: list):
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://mpservice.com/funda91a99886abf7e/release/pages/positionHistory/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            fetchers = [self.fetch_and_save_warehouse(session, tg) for tg in tg_list]
            for finished_task in asyncio.as_completed(fetchers):
                try:
                    await finished_task
                except Exception as e:
                    print(f'Warn:{e}')

    async def fetch_and_save_netval(self, session: aiohttp.ClientSession, tg_info: dict):
        url = 'https://uni-fundts.1234567.com.cn/dataapi/IATG/FundIAAIChart'
        params = {
            'CODE': tg_info['tg_code'],
            'RANGE': 'ln',
            'ctoken': self.ctoken,
            'appVersion': self.app_version,
            'deviceid': self.device_id,
            'passportctoken': self.passport_ctoken,
            'passportid': self.passport_id,
            'passportutoken': self.passport_utoken,
            'plat': 'Iphone',
            'product': 'Fund',
            'serverversion': self.app_version,
            'userid': self.user_id,
            'utoken': self.utoken,
            'version': self.app_version
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            date, netVal, bench_netVal = await parse_netval(json_response, tg_info)
            file = os.path.join(self.folder_name, tg_info['adviser_name'], tg_info['tg_name'], 'netval.csv')
            save_to_csv(file, date=date, SE=netVal, BENCH_SE=bench_netVal)

    async def fetch_and_save_warehouse(self, session: aiohttp.ClientSession, tg_info: dict):
        url = 'https://uni-fundts.1234567.com.cn/combine/investAdviserInfo/getAdjustWarehouse'
        params = {
            'tgCode': tg_info['tg_code'],
            'RANGE': 'ln',
            'ctoken': self.ctoken,
            'appVersion': self.app_version,
            'deviceid': self.device_id,
            'passportctoken': self.passport_ctoken,
            'passportid': self.passport_id,
            'passportutoken': self.passport_utoken,
            'plat': 'Iphone',
            'product': 'Fund',
            'serverversion': self.app_version,
            'tag': '1',
            'userid': self.user_id,
            'utoken': self.utoken,
            'version': self.app_version
        }
        async with session.get(url, params=params) as response:
            json_response = await response.json()
            date, fund_type, ratio, classify_fund = await parse_warehouse(json_response, tg_info)
            file = os.path.join(self.folder_name, tg_info['adviser_name'], tg_info['tg_name'], 'warehouse.csv')
            save_to_csv(file, date=date, type=fund_type, totalratio=ratio, fundlist=classify_fund)

    async def fetch_and_save_extend_info(self, session: aiohttp.ClientSession, tg_info: dict):
        url = 'https://uni-fundts.1234567.com.cn/merge/m/api/tgfund'
        fields = "ACCOUNTID,MINEXPANNSYL,INVEST_TERM,EXPECT_MAX_RETREAT,MAXEXPANNSYL,SHTIME,JJGSID,VIDEO_IMAGE_URL,ENDTIME,STARTTIME,TARGETPROFIT,TARGETANNYIELD,ANNSYL_LN,SYL_D,SHOW_TYPE,SYRQ,HEAD_DISPLAY_TYPE,HEAD_FIELD1,FIELD1_EXPLAIN,HEAD_FIELD2,FIELD2_EXPLAIN,PERFORMANCE1_DISPLAY_TYPE,BENCHMARK_INDEX,PERFORMANCE2_DISPLAY_TYPE,IS_PREVIOUS_INCOME_DISPLAY,IS_TRADE_POSITION_SHOW,QUOTA_DISPLAY,PEOPLENUM_DISPLAY,FEATURE_EXPLAIN,LABEL1,LABEL2,LABEL3,LABEL4,RECOMMEND_HOLD_TIME,STRATEGY_CONCEPT1,STRATEGY_CONCEPT2,STRATEGY_CONCEPT3,IMG_URL,JUMP_TYPE,SELECT_TYPE,KEY_TITLE1,HOLD_LIMIT1,PARTNER,TGNAME,LOGO_NAME,LOGO_URL,BUY_CFM_DAYS,ESTABDATE,RISKLEVEL,STRATEGY_RATE,SYL_Z,BENCHSYL_Z,SYL_Y,BENCHSYL_Y,SYL_3Y,BENCHSYL_3Y,SYL_6Y,BENCHSYL_6Y,SYL_1N,BENCHSYL_1N,SYL_2N,BENCHSYL_2N,SYL_3N,BENCHSYL_3N,SYL_JN,BENCHSYL_JN,SYL_LN,BENCHSYL_LN,STYPE,BUYSTATUS,SERVICE_RATE_TYPE,STEP_RATE,STRATEGY_RATE_DISCOUNT,MINBUY,STGCONCEPT,FEATURE_EXPLAIN,OPERATETIME,OPERAENDTIME,PROVISION_TYPE,PROFIT_DAYS,REDEEM_CFM_DAYS,CASH_BAG_DAYS,CASH_DAYS,COLLECT_TYPE,SERVICE_DESC,BASIC_CAL_FORMULA_REMARK,SUPPORT_RATION,RUN_STATUS,END_STATUS,MAX_RUN_DATE,ACTUAL_RUN_DATE,STATUS,SAME_FUND"
        data = {
            'appVersion': self.app_version,
            'ctoken': self.ctoken,
            'deviceid': self.device_id,
            'fields': fields,
            'pageIndex': 1,
            'pageSize': 3,
            'passportctoken': self.passport_ctoken,
            'passportid': self.passport_id,
            'passportutoken': self.passport_utoken,
            'plat': 'Iphone',
            'product': 'Fund',
            'serverversion': self.app_version,
            'tgCode': tg_info['tg_code'],
            'userid': self.user_id,
            'utoken': self.utoken,
            'version': self.app_version
        }
        async with session.post(url, data=data) as response:
            json_response = await response.json()
            row_name_list, row_value_list = await parse_extend_info(json_response, tg_info)
            file = os.path.join(self.folder_name, tg_info['adviser_name'], tg_info['tg_name'], 'basic_info.csv')
            save_to_csv(file, info=row_name_list, value=row_value_list)

    async def run(self):
        advisers = self.get_advisers_info()
        all_adviser_strategy_info = await self.get_all_strategies(advisers)
        await self.execute_fetch_netval(all_adviser_strategy_info)
        await self.execute_fetch_warehouse(all_adviser_strategy_info)
        await self.execute_fetch_extend_info(all_adviser_strategy_info)
