import time

import requests


url = "https://m.mcloud.139.com/portal/cloudDisk/index.html?path=National_luckyKoi&sourceid=1001&enableShare=1&token=YZsidssolg443eeb7d19a604975d91a869f5c5881e"
HOST = "https://m.mcloud.139.com"
cookies = {
    "hecaiyundata2021jssdkcross": "",
}

def getInfo():
    path = "/ycloud/task-service/task/api/national/luckyKoi/queryTaskInfo"
    url = HOST + path
    data = {"marketName": "National_luckyKoi"}
    headers = {
      "jwttoken": "eyJhbGciOiJ",
      "showloading": "true",
      "user-agent": "Mozilla/5.0 (Linux; Android 12; PDYT20 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 MCloudApp/11.1.1 AppLanguage/zh-CN",
      "content-type": "application/json;charset=UTF-8",
      "accept": "*/*",
      "origin": "https://m.mcloud.139.com",
      "x-requested-with": "com.chinamobile.mcloud",
      "sec-fetch-site": "same-origin",
      "sec-fetch-mode": "cors",
      "sec-fetch-dest": "empty",
      "referer": "https://m.mcloud.139.com/portal/cloudDisk/index.html?path=National_luckyKoi&sourceid=1001&enableShare=1",
      "accept-encoding": "gzip, deflate",
      "accept-language": "zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    res = requests.post(url, headers=headers, cookies=cookies, json=data)
    print(res.status_code)
    print(res.headers)
    print(res.text)


def lottery():
    path = "/ycloud/task-service/task/api/lottery"
    url = HOST + path
    data = {"marketName": "National_luckyKoi", "taskId": 3793}
    headers = {
      "jwttoken": "eyJhbGciOiJIUzI1NiJ9.",
      "showloading": "true",
      "user-agent": "Mozilla/5.0 (Linux; Android 12; PDYT20 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 MCloudApp/11.1.1 AppLanguage/zh-CN",
      "content-type": "application/json;charset=UTF-8",
      "accept": "*/*",
      "origin": "https://m.mcloud.139.com",
      "x-requested-with": "com.chinamobile.mcloud",
      "sec-fetch-site": "same-origin",
      "sec-fetch-mode": "cors",
      "sec-fetch-dest": "empty",
      "referer": "https://m.mcloud.139.com/portal/cloudDisk/index.html?path=National_luckyKoi&sourceid=1001&enableShare=1",
      "accept-encoding": "gzip, deflate",
      "accept-language": "zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    res = requests.post(url, headers=headers, cookies=cookies, json=data)
    print(res.status_code)
    print(res.headers)
    print(res.text)


def getTyrzToken():
    pass


def getEndTimeAndRule():
    url = "https://m.mcloud.139.com/market/manager/commonMarketconfig/getByMarketName?marketName=National_luckyKoi"
    cookies = {
        "hecaiyundata2021jssdkcross": "",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 12; PDYT20 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 MCloudApp/11.1.1 AppLanguage/zh-CN",
        "jwttoken": "eyJhbGciOiJIUzI1NiJ9.",
        "accept": "*/*",
        "x-requested-with": "com.chinamobile.mcloud",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://m.mcloud.139.com/portal/cloudDisk/index.html?path=National_luckyKoi&sourceid=1001&enableShare=1",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    res = requests.get(url, headers=headers, cookies=cookies)
    print(res.text)

for i in range(100):
    lottery()
    time.sleep(1)
# getInfo()


# 0 === e.code ? Fe() : 10001 === e.code ? _.value.status = -
#                                 1 : 400 === e.code ? H.invalidPop = !0 : 10010020 ===
#                                 e.code ? U(
#                                     "很抱歉!<br/>您本月暂无法参与本活动，如有疑问请通过”移动云盘APP-我的-更多服务-在线客服”进行反馈，谢谢。"
#                                 ) : Object(T["c"])(e.msg) ? U(Object(T["c"])(e.msg)) :
#                                 U(e.msg)
