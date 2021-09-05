import time
import uuid

import requests
import os
import json

from selenium.webdriver import DesiredCapabilities

try:
    import cookielib
except:
    import http.cookiejar as cookielib
try:
    from PIL import Image
except:
    pass
from pyzbar.pyzbar import decode
import qrcode
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

header = {
    'referer': 'https://mp.weixin.qq.com/',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
}

LoginHeader = {
    "userlang": "zh_CN",
    "cookie_forbidden": '0',
    "cookie_cleaned": "0",
    "plugin_used": "0",
    "login_type": "3",
    "token": "",
    "lang": "zh_CN",
    "f": "json",
    "ajax": "1",
}
cookie = {}


def get_session():
    phantomJSdriver = '/Users/zhouchao/Documents/phantomjs-2.1.1-macosx/bin/phantomjs'
    os.environ["webdriver.phantomjs.driver"] = phantomJSdriver
    options = webdriver.ChromeOptions()
    capability = webdriver.DesiredCapabilities().INTERNETEXPLORER
    capability['acceptSslCerts'] = True
    driver = webdriver.Chrome(executable_path='/Users/zhouchao/Documents/chromedriver', chrome_options=options, desired_capabilities=capability)
    # driver = webdriver.PhantomJS(phantomJSdriver)
    driver.get('https://mp.weixin.qq.com/?token=&lang=zh_CN')
    driver.wait = WebDriverWait(driver, 20)
    # 从文件中加载cookies(LWP格式)
    session = requests.session()
    session.get('https://mp.weixin.qq.com/?token=&lang=zh_CN')
    print(session.cookies)
    for elem in driver.get_cookies():
        print(elem)
        # requests.utils.add_dict_to_cookiejar(session.cookies, cookie)
        cookie[elem['name']] = elem['value']
    add_other_kv(cookie)
    print(cookie)

    session.cookies.update(requests.utils.cookiejar_from_dict(cookie))
    session.headers.update(header)
    driver.close()
    return session


def add_other_kv(cookie):
    if 'uuid' not in cookie:
        # problem will occur
        cookie['uuid'] = uuid.uuid4().__str__().replace('-', '')
    cookie['rewardsn'] = ''
    cookie['wxtokenkey'] = '777'
    cookie['mm_lang'] = 'zh_CN'


def show_qr_code():
    header_2 = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://mp.weixin.qq.com/?token=&lang=zh_CN',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'macOS',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    }
    url = 'https://mp.weixin.qq.com/cgi-bin/scanloginqrcode'
    print(url)
    qr = session.get(url, cookies=cookie, headers=header_2,
                     params={'action': 'getqrcode', 'random': round(time.time() * 1000)})
    if qr.content is None or qr.content.__len__().__eq__(0):
        print("获取不到二维码")
        exit(1)

    with open('QR.jpg', 'wb') as f:
        f.write(qr.content)
        f.close()

    try:
        im = Image.open(os.path.abspath('QR.jpg'))
        barcodes = decode(im)
        for barcode in barcodes:
            barcode_url = barcode.data.decode("utf-8")
        print(barcode_url)
        qr = qrcode.QRCode()
        qr.add_data(barcode_url)
        qr.print_ascii(invert=True)
        im.show()
        # im.close()
    except:
        print(u'请到 %s 目录找到QR.jpg 手动输入' % os.path.abspath('QR.jpg'))
        input('扫码完成后请输入回车继续')


def login():
    check_url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login'
    response = session.post(check_url, headers=LoginHeader, allow_redirects=False)
    if response.ok and json.dumps(response.json()['base_resp']['err_msg']).__ne__('ok'):
        show_qr_code()
        if (os.path.exists(os.path.abspath('QR.jpg'))):
            try:
                os.remove(os.path.abspath('QR.jpg'))
                print(u'删除文件 %s 成功' % os.path.abspath('QR.jpg'))
            except:
                print(u'删除文件 %s 失败' % os.path.abspath('QR.jpg'))
    start_time = time.time()
    redirct = ''
    print('请扫码登录')
    while True:
        time.sleep(0.5)
        res = session.get('https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1')
        if res.ok and res.json()['status'] == 1:
            LoginHeader['redirect_url'] = ''
            redirect_res = session.post(check_url, headers=LoginHeader, allow_redirects=False)
            if redirect_res.ok and 'redirect_url' in redirect_res.json():
                print(u'登录成功, 耗时 %s 秒' % time.time() - start_time)
                break
        if time.time() - start_time > 300:
            start_time = time.time()
            show_qr_code()

    print(redirct)


session = get_session()
login()
