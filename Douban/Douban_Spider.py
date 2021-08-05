# -*-coding:utf8-*-
import random
import requests
import re
import time
import os
import string

# Env环境设置 通知服务
# export DOUBAN_cookie='xxxxxxxxxxxxxx'                            # （少于8页不需要）豆瓣cookie，自行登录抓包;
# export DOUBAN_Keyword='xx@xx@x@xxx'                              # 检索关键词，使用@连接;
# export DOUBAN_page='x'                                           # 豆瓣小组检索页数（过多可能被封ip）;
# export DOUBAN_barkkey='xxxxxxxxxxxxx$xxxxxxxxxxxxxx'             # bark服务,苹果商店自行搜，支持多个用户推送;
# export DOUBAN_IP='ip:port/get'                                   # ip代理池（如果不需要可以自行修改line 98/99）;
# 建议cron */30 * * * *

def get_ip_json(ip):
    return {'http':'http://' + ip}#{'http':'http://' + ip, 'https':'https://' + ip}

def check_ip(proxy_ip):
    check_url = 'http://icanhazip.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        res = requests.get(check_url, headers=headers, proxies=proxy_ip, timeout=3)
        proxyIP = res.text[0:-1]
        # print(proxyIP, proxy_ip['https'].split('//')[1].split(':')[0])
        if (proxyIP == proxy_ip['http'].split('//')[1].split(':')[0]):
            print("Proxy IP:" + proxyIP + " success!")
            return True
        else:
            print("Check: Proxy IP failure!")
            return False
    except Exception as e:
        print("ERROR: Proxy IP failure!", e)
        return False

# 高匿代理一定需要
def get_high_stash_IP():
    ip_url = DOUBAN_IP_GET
    ip = ""
    while True:
        get_json = requests.get(ip_url).json()
        ip =  get_ip_json(get_json["proxy"])
        # print("In While:", ip)
        if check_ip(ip) == True:
            break
        time.sleep(3)
    return ip

def get_random_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua

def get_random_ck():
    twond = str(random.randint(2, 4))
    last = ''.join(str(random.choice(range(7))) for _ in range(7))
    final = ''.join(random.sample(string.digits+string.ascii_letters, 11))
    dbcl2 = '2'+twond+last+':'+final
    bid = ''.join(random.sample(string.digits+string.ascii_letters, 11))
    ck = ''.join(random.sample(string.digits+string.ascii_letters, 4))
    return 'bid=' + bid + '; dbcl2="' + dbcl2 + '"; ck=' + ck

def get_douban_works(num, groupnumber):
    num_norm = num*25
    douban_url = 'https://www.douban.com/group/'+groupnumber+'/discussion?start='+str(num_norm)
    Random_UA = get_random_ua()
    Random_CK = get_random_ck()
    print('Page Group:', groupnumber)
    print("生成随机UA：", Random_UA)

    if "DOUBAN_CK" in os.environ:
        DOUBAN_CK = os.environ["DOUBAN_CK"]
        # print("已获取并使用Env环境，DOUBAN_CK=", DOUBAN_CK)
        print("使用指定CK：", DOUBAN_CK)
    else:
        print("使用随机CK：", Random_CK)

    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Cookie' : Random_CK,
        'Host': 'www.douban.com',
        'Referer': 'https://accounts.douban.com/',
        'User-Agent': Random_UA,
    }

    proxy_IP = get_high_stash_IP()
    douban_res = requests.get(douban_url, headers=headers, proxies=proxy_IP)
    # print(douban_res.text)
    if '检测到有异常请求从你的 IP 发出' in douban_res.text:
        bark_post('IP已被封', '请更换ck或者使用代理ip', DOUBAN_barkkey)
        return []
    else:
        pattern1 = re.compile(r'<td class="title">(.*?)</td>', re.S | re.M)
        rowinfo = pattern1.findall(douban_res.text)
        work_list = []
        for item in rowinfo:
            if "【作业】" in item:
                work_list.append(item)
        return work_list

def get_final_works(page_num):
    work_total_list = []
    for i in range(page_num):
        print("Get Page:", i+1)
        work_total_list.extend(get_douban_works(i,'698716'))
        time.sleep(5)
        work_total_list.extend(get_douban_works(i,'what2buy'))
        time.sleep(5)
    return {}.fromkeys(work_total_list).keys()

def choose_work(list, key_list):
    pattern_title = re.compile(r'title="(.*?)" class="">', re.S | re.M)
    with open("douban_work.txt", "r", encoding='utf-8') as f:  # 打开文件
        data = f.read()
    work_to_send = []
    for item in list:
        for key in key_list:
            if key in item:
                topic = pattern_title.findall(item)[0]
                if topic in data:
                    print("作业已经存在不推送：", topic)
                else:
                    work_to_send.append(item)
                    break
    return work_to_send

def bark_post(Subject, Message, Sckey):
    url = 'https://api.day.app/' + Sckey + '/' + Subject + '?url=' + Message
    print(url)
    r = requests.get(url)

def send_nofity(list, sendkey):
    if list==[]:
        print("无作业！退出")
        return
    pattern_title = re.compile(r'title="(.*?)" class="">', re.S | re.M)
    pattern_href = re.compile(r'<a href="(.*?)" title=', re.S | re.M)
    for item in list:
        print("===============================================")
        topic = pattern_title.findall(item)[0]
        hrefurl = pattern_href.findall(item)[0]
        print(topic)
        print(hrefurl)
        bark_post(topic, hrefurl, sendkey)
        print("推送成功！")
        with open('douban_work.txt', 'r+',newline='',encoding='utf-8') as f:
            content = f.read()
            f.seek(0, 2)
            f.write(topic + '\n')
        print("写入数据成功！")
        time.sleep(5)
    return
 
if __name__ == '__main__':
    if "DOUBAN_Keyword" in os.environ:
        DOUBAN_Keyword = os.environ["DOUBAN_Keyword"]
        DOUBAN_Keyword = DOUBAN_Keyword.split('@')
        print("已获取并使用Env环境，DOUBAN_Keyword=", DOUBAN_Keyword)
    if "DOUBAN_page" in os.environ:
        DOUBAN_page = int(os.environ["DOUBAN_page"])
        print("已获取并使用Env环境，DOUBAN_page=", DOUBAN_page)
    if "DOUBAN_barkkey" in os.environ:
        DOUBAN_barkkey = os.environ["DOUBAN_barkkey"]
        print("已获取并使用Env环境，DOUBAN_barkkey=", DOUBAN_barkkey)
    if "DOUBAN_IP_GET" in os.environ:
        DOUBAN_IP_GET = os.environ["DOUBAN_IP_GET"]
        print("已获取并使用Env环境，DOUBAN_IP_GET=", DOUBAN_IP_GET)

    filename = 'douban_work.txt'
    if os.path.exists(os.getcwd()+'/'+filename)==False:
        print('未找到数据文件，正在为您新建数据文件...')
        file = open('./douban_work.txt', "w")
        file.close()


    final_work = get_final_works(DOUBAN_page)
    final_send = choose_work(final_work, DOUBAN_Keyword)
    send_nofity(final_send, DOUBAN_barkkey)
