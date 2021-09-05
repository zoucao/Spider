import yaml
import os
import sys
from article_url import PublicAccountsWeb
from article_info import ArticlesInfo
from excel import excelUtil
import time

if 'python' in sys.executable:
    abs_path = lambda file: os.path.abspath(os.path.join(os.path.dirname(__file__), file))
else:
    abs_path = lambda file: os.path.abspath(
        os.path.join(os.path.dirname(sys.executable), file))  # mac 上打包后 __file__ 指定的是用户根路径，非当执行文件路径


def load_conf():
    if not os.path.exists(abs_path('config.yaml')):
        print("找不到conf.yaml")
        exit(1)
    return yaml.full_load(open(abs_path('config.yaml'), encoding='utf8'))


def __verify_exist(config, name):
    if config.get(name) is None or config.get(name) is '':
        raise FileExistsError("在config.yaml中找不到" + name)


def check_next_fetch(nick_name, biz, paw, ts, index=0, excel=None, article_info=None):
    article_list = paw.get_urls(nick_name, biz=biz)
    time.sleep(3)
    for article in article_list:
        if article["create_time"] < ts:return;
        title = article["title"]
        date = time.strftime("%Y-%m-%d", time.localtime(int(article["create_time"])))
        start_time = time.strftime("%H:%M:%S", time.localtime(int(article["create_time"])))
        link = article["link"]
        read_num = -1
        try:
             read_num, like_num, old_like_num = article_info.read_like_nums(link)
        except:
            print("文章<{}>获取不了阅读量".format(title))

        print("title: {0} , time: {1} , link: {2}, read_num: {3}.".format(title,
                                                          start_time,
                                                          link,
                                                          read_num))
        if excel is not None:
            excel.add_column(date, nick_name, title, link, read_num, start_time)
    if len(article_list) < 5: return;
    check_next_fetch(nick_name, biz, paw, ts, index + 5)


if __name__ == "__main__":
    time_range = input("请输入截止日期.") #"2021-09-04"
    timeArray = time.strptime(time_range + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(timeArray))
    mode = input("选择模式:\n1.config获取cookie.\n2.手动输入cookie.")
    conf = load_conf()
    if mode == '1':
        __verify_exist(conf.get("wechat_platform"), "cookie")
        __verify_exist(conf.get("wechat_platform"), "token")
        platform_cookie = conf.get("wechat_platform").get("cookie")
        token = conf.get("wechat_platform").get("token")
        __verify_exist(conf.get("wechat_app"), "cookie")
        __verify_exist(conf.get("wechat_app"), "appmsg_token")
        app_cookie = conf.get("wechat_app").get("cookie")
        app_token = conf.get("wechat_app").get("appmsg_token")
    elif 2:
        platform_cookie = input("请输入输入cookie.")
        token = input("请输入token.")
        app_cookie = input("请输入输入cookie.")
        app_token = input("请输入token.")
    else:
        raise Exception("识别不了模式，请输入 1 或 2 ")
    paw = PublicAccountsWeb(cookie=platform_cookie, token=token)
    article_info = ArticlesInfo(app_token, app_cookie)
    excel = excelUtil()
    excel.init_sheet()
    name_list = conf.get("nick_name")
    for dic in name_list:
        nick_name = dic.get("name")
        biz = dic.get('biz')
        print("----------------------------------------------------")
        print(u"公众号:%s" % nick_name)
        check_next_fetch(nick_name, biz if biz != "" else None, paw, ts, excel=excel, article_info=article_info)
    excel.save()
