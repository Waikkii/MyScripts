# -*-coding:utf8-*-
import random
import requests
import re
# from fake_useragent import UserAgent
import time
import os

# Env环境设置 通知服务
# export DOUBAN_Keyword='[xx,xx,x,xxx]'             # 检索关键词;
# export DOUBAN_page='x'                            # 豆瓣小组检索页数（过多可能被封ip）;
# export DOUBAN_barkkey='xxxxxxxxxxxxx'             # bark服务,苹果商店自行搜;


def get_high_stash_IPs():
    ip_num = 30
    ip_url = 'http://www.xiladaili.com/api/?uuid=92968207a8d44443b4305cae050901c4&num='+str(ip_num)+'&place=中国&category=1&protocol=2&sortby=0&repeat=1&format=3&position=1' 
    print('IP url is: ', ip_url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    }
    get_json = requests.get(ip_url, headers=headers).text
    return get_json.split(' ')

def get_random_proxies(ip_list):
    proxy_list = []
    random.shuffle(ip_list)
    for i in range(len(ip_list)):
        proxy_one = {'http':'http://' + ip_list[i], 'https':'https://' + ip_list[i]}
        proxy_list.append(proxy_one)
    return proxy_list

def check_ip(proxy_list):
    proxy_checked_list = []
    check_url = 'http://icanhazip.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    for item in proxy_list:
        try:
            requests.adapters.DEFAULT_RETRIES = 3
            res = requests.get(check_url, headers=headers, proxies=item, timeout=3)
            proxyIP = res.text[0:-1]
            print(proxyIP, item['https'].split('//')[1].split(':')[0])
            if (proxyIP == item['https'].split('//')[1].split(':')[0]):
                print("Proxy IP:'" + proxyIP + " success!")
                proxy_checked_list.append(item)
            else:
                print("Check: Proxy IP failure!")
        except Exception as e:
            print("ERROR: Proxy IP failure!", e)
    return proxy_checked_list

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

def get_douban_works(num):
    num_norm = (num-1)*25
    douban_url = 'https://www.douban.com/group/698716/discussion?start='+str(num_norm)
    # try:
    #     Random_UA = UserAgent().random
    # except:
    #     Random_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'

    # Random_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    Random_UA = get_random_ua()
    print("生成随机UA：", Random_UA)

    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': Random_UA
    }
    douban_res = requests.get(douban_url, headers=headers)
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
        work_total_list.extend(get_douban_works(i))
        time.sleep(3)
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
    # 高匿代理暂时不需要
    # IP_list = get_high_stash_IPs()
    # RANDOM_IP_LIST = get_random_proxies(IP_list)
    # CHECKED_IP_LIST = check_ip(RANDOM_IP_LIST)


    if "DOUBAN_Keyword" in os.environ:
        DOUBAN_Keyword = os.environ["DOUBAN_Keyword"]
        DOUBAN_Keyword = DOUBAN_Keyword.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
        print("已获取并使用Env环境，DOUBAN_Keyword=", DOUBAN_Keyword)
    if "DOUBAN_page" in os.environ:
        DOUBAN_page = int(os.environ["DOUBAN_page"])
        print("已获取并使用Env环境，DOUBAN_page=", DOUBAN_page)
    if "DOUBAN_barkkey" in os.environ:
        DOUBAN_barkkey = os.environ["DOUBAN_barkkey"]
        print("已获取并使用Env环境，DOUBAN_barkkey=", DOUBAN_barkkey)

    filename = 'douban_work.txt'
    if os.path.exists(os.getcwd()+'/'+filename)==False:
        print('未找到数据文件，正在为您新建数据文件...')
        file = open('./douban_work.txt', "w")
        file.close()


    final_work = get_final_works(DOUBAN_page)
    final_send = choose_work(final_work, DOUBAN_Keyword)
    send_nofity(final_send, DOUBAN_barkkey)
