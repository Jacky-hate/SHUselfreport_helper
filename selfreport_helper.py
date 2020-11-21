from urllib import request, parse
import urllib
from io import BytesIO
import gzip
import http.cookiejar
import time
import socket
import re
import base64
from urllib.parse import quote


def post(year, month, day, half, head):
    time = "{}-{:0>2d}-{:0>2d}".format(year, month, day)
    url_des = "https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day=" + time + "&t=" + str(half)
    head = {
        "Host": "selfreport.shu.edu.cn",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Referer": "https://selfreport.shu.edu.cn/XueSFX/HalfdayReport_History.aspx",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": head["Cookie"],
    }
    req = request.Request(url=url_des, headers=head, method='GET')
    response = request.urlopen(req, timeout=2)
    # print(response.status, response.reason)
    # for key, values in response.getheaders():
    #     print(key + " " + values)
    buff = BytesIO(response.read())
    f = gzip.GzipFile(fileobj=buff)
    htmls = f.read().decode('utf-8')
    s = str(htmls)
    pattern = re.compile(r'id="__VIEWSTATE" value="(.*?)"')
    result_vs = str(re.findall(pattern, s)[0])
    result_vs = quote(result_vs, 'utf-8')
    pattern = re.compile(r'id="__VIEWSTATEGENERATOR" value="(.*?)"')
    result_vsg = str(re.findall(pattern, s)[0])
    result_vsg = quote(result_vsg, 'utf-8')
    result_base64 = '{"p1_BaoSRQ":{"Text":"' + time + '"},"p1_DangQSTZK":{"F_Items":[["良好","良好",1],["不适","不适",1]],"SelectedValue":"良好"},"p1_ZhengZhuang":{"Hidden":true,"F_Items":[["感冒","感冒",1],["咳嗽","咳嗽",1],["发热","发热",1]],"SelectedValueArray":[]},"p1_SuiSM":{"F_Items":[["红色","红色",1],["黄色","黄色",1],["绿色","绿色",1]],"SelectedValue":null},"p1_ShiFJC":{"F_Items":[["早餐","早餐",1],["午餐","午餐",1],["晚餐","晚餐",1]],"SelectedValueArray":[]},"p1_ctl00_btnSubmit":{"Hidden":false},"p1":{"Title":"每日两报（下午）","IFrameAttributes":{}}}'
    result_base64 = result_base64.encode("utf-8")
    result_base64 = base64.b64encode(result_base64)
    result_base64 = result_base64.decode('utf-8')
    r = quote(result_base64, 'utf-8')
    r = r[0:414] + 'F_STATE' + r[414:824]
    head = {
        "Host": "selfreport.shu.edu.cn",
        "Connection": "keep-alive",
        "Content-Length": " 1446",
        "Accept": " text/plain, */*; q=0.01",
        "X-FineUI-Ajax": " true",
        "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": " https://selfreport.shu.edu.cn",
        "Referer": " https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day=2020-11-19&t=1",
        "Accept-Encoding": " gzip, deflate, br",
        "Cookie": head["Cookie"],
    }
    data = bytes(
        "__EVENTTARGET=p1%24ctl00%24btnSubmit&__EVENTARGUMENT=&__VIEWSTATE=" + result_vs + "&__VIEWSTATEGENERATOR=" + result_vsg + "&p1%24ChengNuo=p1_ChengNuo&p1%24BaoSRQ=" + time + "&p1%24DangQSTZK=%E8%89%AF%E5%A5%BD&p1%24TiWen=37&p1%24SuiSM=%E7%BB%BF%E8%89%B2&F_TARGET=p1_ctl00_btnSubmit&p1_Collapsed=false&F_STATE=" + r,
        encoding='utf8')
    head["Content-Length"] = str(len(data))
    head["Referer"] = url_des
    req = request.Request(url=url_des, headers=head, method='POST', data=data)
    try:
        response = request.urlopen(req, timeout=2)
        print(time, " ", response.reason)
        # for key, values in response.getheaders():
        #     print(key + " " + values)
        buff = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buff)
        htmls = f.read().decode('utf-8')
    except socket.timeout:
        print(time + "time out")

    # print(htmls)


class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib.request.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result

    http_error_301 = http_error_303 = http_error_307 = http_error_302


opener = urllib.request.build_opener(RedirectHandler())
urllib.request.install_opener(opener)


def init():
    username = input("please tape in your username: ")
    password = input("please tape in your password: ")

    start_url = "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ== "

    head = {
        "Host": "newsso.shu.edu.cn",
        "Connection": "keep-alive",
        "Content-Length": "51",
        "Origin": "https://newsso.shu.edu.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Referer": "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ==",
        "Cookie": "",
    }
    data = {
        "username": str(username),
        "password": str(password),
        "login_submit": ""
    }
    data = bytes(parse.urlencode(data), encoding='utf8')
    head["Content-Length"] = str(len(data))
    req = request.Request(url=start_url, data=data, headers=head, method='POST')
    response = request.urlopen(req, timeout=2)
    head = {
        "Host": "newsso.shu.edu.cn",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Referer": "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ==",
        "Cookie": "",
    }
    print(response.status, response.reason)
    # print(response.read().decode())
    for key, values in response.getheaders():
        if key == 'set-cookie':
            head['Cookie'] = values
        if key == 'location':
            url2 = "https://" + head['Host'] + values
    req = request.Request(url=url2, headers=head, method='GET')
    response = request.urlopen(req, timeout=2)
    head = {
        "Host": "selfreport.shu.edu.cn",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Referer": "https://newsso.shu.edu.cn/",
        # "Cookie": "",
    }
    print(response.status, response.reason)
    for key, values in response.getheaders():
        if key == 'location':
            url3 = values
    req = request.Request(url=url3, headers=head, method='GET')
    response = request.urlopen(req, timeout=2)
    head = {
        "Host": "selfreport.shu.edu.cn",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
        "Referer": "https://newsso.shu.edu.cn/",
        "Cookie": "",
    }
    print(response.status, response.reason)
    for key, values in response.getheaders():
        if key == 'location':
            url3 = head['Host'] + values
        if key == 'Set-Cookie':
            head['Cookie'] = values
    url4 = "https://selfreport.shu.edu.cn/Default.aspx"
    req = request.Request(url=url4, headers=head, method='GET')
    response = request.urlopen(req, timeout=2)
    print(response.status, response.reason)
    for key, values in response.getheaders():
        print(key + " " + values)
    print("下面开始填报：")
    t = input("Set interval time(s): ")
    t = float(t)
    for i in [10, 11]:
        for j in range(32):
            for k in [1, 2]:
                post(2020, i, j, k, head)
                time.sleep(t)


f = 1
while f == 1:
    try:
        f = 0
        init()
    except NameError:
        print("密码错误,请重试...")
        f = 1
    except urllib.error.URLError:
        print("网络限制，请更换网络或稍候再试...")
    except:
        print("发生未知错误，请联系管理员:sowhata@vip.qq.com ")
input("Tap to exit...")
time.sleep(1)

# data = {
#     "__EVENTTARGET": "p1%24ctl00%24btnSubmit",
#     "__EVENTARGUMENT": "",
#     "__VIEWSTATE": "WDi3E2rKu63MQJjMdlmxSg5VBLbYOw4%2FAgEw1IpkHYe0lmbEWgdBypP6%2B%2FEC656BhWGiLuoM9W454EHaYAx3cq3MgXEnMJRrmWPhn5Kc5UqC4mNubdpvjQZmHTztgILFVP%2BOd9mlpHa5%2Bbi25fXZeKS2Mv5ZHIQLJZIFVuA2txVwLPer5cLcICb%2Fj%2F7n0BxjawHHODS954surwn7P12HxBSEObuixfXVZSPAAaFr%2F7hfFgL2NeWl9qz6aS8yTChrRIcSW4insfUIUPq35fKiYJCuhTVVUvenINvcYApaUOnTwxQ13jhQp81WmGCyMBaw",
#     "__VIEWSTATEGENERATOR": "DC4D08A3",
#     "p1%24ChengNuo": "p1_ChengNuo",
#     "p1%24BaoSRQ": "2020-11-19",
#     "p1%24DangQSTZK": "%E8%89%AF%E5%A5%BD",
#     "p1%24TiWen": "37",
#     "p1%24SuiSM": "%E7%BB%BF%E8%89%B2",
#     "F_TARGET": "p1_ctl00_btnSubmit",
#     "p1_Collapsed": "false",
#     "F_STATE": "eyJwMV9CYW9TUlEiOnsiVGV4dCI6IjIwMjAtMTEtMTkifSwicDFfRGFuZ1FTVFpLIjp7IkZfSXRlbXMiOltbIuiJr%2BWlvSIsIuiJr%2BWlvSIsMV0sWyLkuI3pgIIiLCLkuI3pgIIiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6IuiJr%2BWlvSJ9LCJwMV9aaGVuZ1podWFuZyI6eyJIaWRkZW4iOnRydWUsIkZfSXRlbXMiOltbIuaEn%2BWGkiIsIuaEn%2BWGkiIsMV0sWyLlkrPll70iLCLlkrPll70iLDFdLFsi5Y%2BR54OtIiwi5Y%2BR54OtIiwxXV0sIlNlbGVjdGVkVmFsdWVBcnJheSI6W119LCJwMV9TdWlTTSI6eyJGX0l0ZW1zIjpbWyLnuqLoibIiF_STATELCLnuqLoibIiLDFdLFsi6buE6ImyIiwi6buE6ImyIiwxXSxbIue7v%2BiJsiIsIue7v%2BiJsiIsMV1dLCJTZWxlY3RlZFZhbHVlIjpudWxsfSwicDFfU2hpRkpDIjp7IkZfSXRlbXMiOltbIuaXqemkkCIsIuaXqemkkCIsMV0sWyLljYjppJAiLCLljYjppJAiLDFdLFsi5pma6aSQIiwi5pma6aSQIiwxXV0sIlNlbGVjdGVkVmFsdWVBcnJheSI6W119LCJwMV9jdGwwMF9idG5TdWJtaXQiOnsiSGlkZGVuIjpmYWxzZX0sInAxIjp7IlRpdGxlIjoi5q%2BP5pel5Lik5oql77yI5LiL5Y2I77yJIiwiSUZyYW1lQXR0cmlidXRlcyI6e319fQ%3D%3D"
# }
