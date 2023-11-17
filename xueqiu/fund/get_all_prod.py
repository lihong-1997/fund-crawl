import requests
from itertools import product
import IPython
if IPython.get_ipython() is not None:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

cookies = {
    'device_id': 'web_rJzzsBv02',
    'timestamp': '1694093236407',
    'Authorization': 'OAuth2 2103100008c141676750db5e24f69c9c515e6dfc8e6a864e8',
    'acw_tc': '2760820e16940920424201456e2f829106b6caaede1ea5f71f5df438b71a55',
    'device_id': 'web_rJzzsBv02',
    'timestamp': '1694092374968',
    'u': '962421832',
    'xq_a_token': 'c4cd4ab197190bb1d3398c9c8a70586117732267',
    'Hm_lpvt_d8a99640d3ba3fdec41370651ce9b2ac': '1694093234',
    'Hm_lvt_d8a99640d3ba3fdec41370651ce9b2ac': '1694092204',
    'Authorization': 'OAuth2 2103100008c141676750db5e24f69c9c515e6dfc8e6a864e8',
    'u': '962421832',
    'xq_a_token': 'c4cd4ab197190bb1d3398c9c8a70586117732267',
    'channel': '',
    'h5_channel': '',
    'acw_tc': '2760820e16940920424201456e2f829106b6caaede1ea5f71f5df438b71a55',
}

q1 = ["A", "B", "C", "D"]
q2 = ["A", "B", "C"]
q3 = ["A", "B", "C", "D"]
q4 = ["A", "B", "C", "D", "E"]


def get_all_prod():
    headers = {
        'Host': 'danjuanfunds.com',
        'Accept': 'application/json, text/plain, */*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://danjuanfunds.com',
        'User-Agent': 'Fund iPhone 7.20 ;Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'elastic-apm-traceparent': '00-503d0297e3bf2ec9b4dcb7d85f862bcb-2d6df6c614ff26fa-01',
        'Referer': 'https://danjuanfunds.com/KYCAssessment?tp_company_no=-1&source=ic',
        'Sec-Fetch-Dest': 'empty',
    }
    codes = set()
    with tqdm(total=240, desc="获取策略信息中") as pbar:
        for item1, item2, item3, item4 in product(q1, q2, q3, q4):
            json_data = {
                'tp_company_no': '-1',
                'answers': f'1{item1};2{item2};3{item3};4{item4}',
            }
            response = requests.post('https://danjuanfunds.com/djapi/fundx/portfolio/ic/plan/kyc/answer', cookies=cookies, headers=headers, json=json_data,)
            headers = {
                'dj-device-id': 'DJ_2459B45B-599C-46A3-9D25-CDBF4B023114',
                'dj-version': '7.20',
                'dj-sys-version': 'iOS 16.5.1',
                'dj-client': 'iOS',
                'User-Agent': 'Fund iPhone 7.20',
                'Authorization': 'OAuth2 2103100008c141676750db5e24f69c9c515e6dfc8e6a864e8',
            }
            params = {'_s': '97c30d'}
            response = requests.get('https://fund.xueqiu.com/fundx/portfolio/ic/plan/shelf/page', params=params, headers=headers)
            res = response.json()
            code_set = {(item["ic_plan_code"], item["ic_plan_name"]) for item in res['data']['items']}
            codes = (codes | code_set)
            pbar.update(1)

    prod_list = [{"code": k, "name": v} for k, v in codes]
    return prod_list
