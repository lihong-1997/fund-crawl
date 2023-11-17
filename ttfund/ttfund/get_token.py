# coding:utf-8
import requests


class GetToken:

    def __init__(self):

        self.timeout = 5
        self.gtoken = 'A365D353A41044D7A050FFE514D61Ec7'
        self.ctoken = 'Vh-ErBuwkbeMML_mLAR7rauuDHCsU69P2mmb-wH7jBjsa3wqmyxeB42pJ3sj6GFvN9T6io' \
                      '-W3zFeNRXnQlcedYVtSLOtuQGTDFapYKHgv5CBF0I4TH0oG2KK_L0_wlIGASSfVfoi9jYhDtPIreJ2' \
                      'iPdxeqynzfY_ftiFyeiHj19mV8twat_devk_FlklxVWvTy7Kgab7mCS3OYWhmCbihRD919FhXrWGSd0PQMLimKE.15'
        self.device_id = '6427175E-D9A6-4986-B51D-5572F86F1FDA'
        self.app_version = '6.6.4'
        # 以下参数由 param_init 更新
        self.passport_utoken = None
        self.passport_ctoken = None
        self.utoken = None
        self.passport_id = None
        self.user_id = None
        self.param_init_1()

    def param_init_1(self):

        url = 'https://tradeapilvs15.95021.com/User/Account/LoginForMobileReturnContextId'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'tradeapilvs15.95021.com',
            'Referer': 'https://mpservice.com/fundffc6fe53910b4e/release/pages/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        data = {
            'Account': '13680310398',
            'AppType': 'ttjj',
            'CToken': self.ctoken,
            'CertificateType': '0',
            'DeviceName': 'iPhone',
            'DeviceOS': 'iOS 16.4.1',
            'DeviceType': 'IOS16.4.1',
            'GTOKEN': self.gtoken,
            'MobileKey': self.device_id,
            'Password': 'dab23ab665068278390195666652a9ab',
            'PhoneType': 'Iphone',
            'ServerVersion': self.app_version,
            'Version': '4.6.0'
        }
        try:
            response = requests.post(url=url, headers=headers, data=data, timeout=self.timeout)
        except Exception as e:
            print("Error occurs while getting token, ", e)
        else:
            # 解析json
            json_response = response.json()
            self.user_id = json_response['Data']['CustomerNo']
            self.passport_id = json_response['Data']['PassportID']
            self.ctoken = json_response['Data']['CToken']
            self.utoken = json_response['Data']['UToken']
            self.param_init_2()

    def param_init_2(self):

        url = 'https://tradeapilvs15.95021.com/User/Passport/PLogin'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'tradeapilvs15.95021.com',
            'Referer': 'https://mpservice.com/8543c2ac1ae2a93335b443a3f9f1028f/release/pages/index/index',
            'clientInfo': 'ttjj-iPhone 13 Pro-iOS-iOS16.4.1',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9, de-CN;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'EMProjJijin/6.6.4 (iPhone; iOS 16.4.1; Scale/3.00)',
            'GTOKEN': self.gtoken
        }
        data = {
            'CToken': self.ctoken,
            'CustomerNo': self.user_id,
            'MobileKey': self.device_id,
            'PhoneType': 'Iphone',
            'ServerVersion': self.app_version,
            'UToken': self.utoken,
            'UsrId': self.user_id,
            'Version': '4.6.0',
            'ctoken': self.ctoken,
            'userid': self.user_id,
            'utoken': self.utoken
        }
        try:
            response = requests.post(url=url, headers=headers, data=data, timeout=self.timeout)
        except Exception as e:
            print('Error occurs while getting token', e)
        else:
            # 解析json
            json_response = response.json()
            self.passport_ctoken = json_response['Data']['PassportCToken']
            self.passport_utoken = json_response['Data']['PassportUToken']
