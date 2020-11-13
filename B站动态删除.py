# coding=gbk
from selenium import webdriver
#from bs4 import BeautifulSoup
import time,re,jieba,datetime
#from cocoNLP.extractor import extractor
from datetime import datetime, timedelta
from dateutil.parser import parse
import jieba.posseg as psg

UTIL_CN_NUM = {
    '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
}

UTIL_CN_UNIT = {'十': 10, '百': 100, '千': 1000, '万': 10000}


def cn2dig(src):
    if src == "":
        return None
    m = re.match("\d+", src)
    if m:
        return int(m.group(0))
    rsl = 0
    unit = 1
    for item in src[::-1]:
        if item in UTIL_CN_UNIT.keys():
            unit = UTIL_CN_UNIT[item]
        elif item in UTIL_CN_NUM.keys():
            num = UTIL_CN_NUM[item]
            rsl += num * unit
        else:
            return None
    if rsl < unit:
        rsl += unit
    return rsl


def year2dig(year):
    res = ''
    for item in year:
        if item in UTIL_CN_NUM.keys():
            res = res + str(UTIL_CN_NUM[item])
        else:
            res = res + item
    m = re.match("\d+", res)
    if m:
        if len(m.group(0)) == 2:
            return int(datetime.datetime.today().year / 100) * 100 + int(m.group(0))
        else:
            return int(m.group(0))
    else:
        return None


def parse_datetime(msg):
    if msg is None or len(msg) == 0:
        return None

    try:
        dt = parse(msg, fuzzy=True)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        m = re.match(
            r"([0-9零一二两三四五六七八九十]+年)?([0-9一二两三四五六七八九十]+月)?([0-9一二两三四五六七八九十]+[号日])?([上中下午晚早]+)?([0-9零一二两三四五六七八九十百]+[点:\.时])?([0-9零一二三四五六七八九十百]+分?)?([0-9零一二三四五六七八九十百]+秒)?",
            msg)
        if m.group(0) is not None:
            res = {
                "year": m.group(1),
                "month": m.group(2),
                "day": m.group(3),
                "hour": m.group(5) if m.group(5) is not None else '00',
                "minute": m.group(6) if m.group(6) is not None else '00',
                "second": m.group(7) if m.group(7) is not None else '00',
            }
            params = {}

            for name in res:
                if res[name] is not None and len(res[name]) != 0:
                    tmp = None
                    if name == 'year':
                        tmp = year2dig(res[name][:-1])
                    else:
                        tmp = cn2dig(res[name][:-1])
                    if tmp is not None:
                        params[name] = int(tmp)
            target_date = datetime.today().replace(**params)
            is_pm = m.group(4)
            if is_pm is not None:
                if is_pm == u'下午' or is_pm == u'晚上' or is_pm == '中午':
                    hour = target_date.time().hour
                    if hour < 12:
                        target_date = target_date.replace(hour=hour + 12)
            return target_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None


def check_time_valid(word):
    m = re.match("\d+$", word)
    if m:
        if len(word) <= 6:
            return None
    word1 = re.sub('[号|日]\d+$', '日', word)
    if word1 != word:
        return check_time_valid(word1)
    else:
        return word1


# 时间提取
def time_extract(text):
    time_res = []
    word = ''
    keyDate = {'今天': 0, '明天': 1, '后天': 2}
    for k, v in psg.cut(text):
        if k in keyDate:
            if word != '':
                time_res.append(word)
            word = (datetime.today() + timedelta(days=keyDate.get(k, 0))).strftime('%Y{y}%m{m}%d{d}').format(y='年',m='月',d='日')

        elif word != '':
            if v in ['m', 't']:
                word = word + k
            else:
                time_res.append(word)
                word = ''
        elif v in ['m', 't']:
            word = k
    if word != '':
        time_res.append(word)
    result = list(filter(lambda x: x is not None, [check_time_valid(w) for w in time_res]))
    final_res = [parse_datetime(w) for w in result]

    return [x for x in final_res if x is not None]

########################################################################################################################
#单次循环测试
'''
#ex = extractor()
driver = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
driver.get("https://www.bilibili.com/")
time.sleep(3)
driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/div[1]/div/span/div/span').click()
time.sleep(20) #第一步等待时长为20秒，有需求自己改
driver.get('https://space.bilibili.com/')
time.sleep(5)
driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/div[1]/a[2]').click()
i = 0
js = "window.scrollTo(0,99999999);"
while i < 5:#页面加载长度
    i +=1
    time.sleep(3)
    driver.execute_script(js)

list_time = []
list_text = []
list_id = []
#页面隐藏内容激发
origin_page = driver.find_elements_by_class_name('fold-text')
for p in origin_page:
    time.sleep(1)
    p.click()
origin = driver.find_elements_by_class_name('expand-btn')
for o in origin:
    time.sleep(1)
    o.click()
time.sleep(1)
#转发动态文本获取
text = driver.find_elements_by_class_name('card')
time.sleep(2)
for t in text:
    part_text = t.get_attribute('innerText')
    real_t = re.sub('[a-zA-z]', '', part_text)
    list_text.append(real_t)
list_text=[x for x in list_text if x!='']
time.sleep(3)
#转发动态的id获取
id = driver.find_elements_by_xpath('//div[@class="post-content repost"]')
for e in id:
    list_id.append(e.get_attribute('data-ori-did'))
print(list_id)
time.sleep(3)
#文本日期识别


for te in list_text:
    try:
        #times = ex.extract_time(te)
        print(te)
        times = time_extract(te)
        list_te = []
        for tim in times:
            list_te.append(tim[5:10])
        print(max(list_te))
        max_t = max(list_te)
        real_time = '2020' + f'{max_t[0:2]}' + f'{max_t[3:5]}'
        rel_time = int(real_time)
        print(real_time)
        list_time.append(rel_time)
        time.sleep(3)
    except:
        list_time.append(20201231)

print(list_text)
print(list_time)
print(list_id)


#fp = open('./需要删除的id.txt','w',encoding='utf-8')
wrong_id_list = []
time_real = 20201112 #当前日期请输入 eg：2020年11月12日写为20201112
n_id = 0
for t in list_time:
    if t < time_real:
        wrong_id_list.append(list_id[n_id])
        # fp.write(list_id[n_id])
    else:
        pass
    n_id += 1
print(wrong_id_list)
'''
########################################################################################################################
#循环遍历到最后
while True:
    #ex = extractor()
    driver = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
    driver.get("https://www.bilibili.com/")
    time.sleep(3)
    driver.find_element_by_xpath(
        '/html/body/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/div[1]/div/span/div/span').click()
    time.sleep(20) #第一步等待时长为20秒，有需求自己改
    driver.get('https://space.bilibili.com/')
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/div[1]/a[2]').click()
    i = 0
    js = "window.scrollTo(0,99999999);"
    while i < 50:  # 页面加载长度
        i += 1
        time.sleep(3)
        driver.execute_script(js)

    list_time = []
    list_text = []
    list_id = []
    # 页面隐藏内容激发
    origin_page = driver.find_elements_by_class_name('fold-text')
    for p in origin_page:
        time.sleep(1)
        p.click()
    origin = driver.find_elements_by_class_name('expand-btn')
    for o in origin:
        time.sleep(1)
        o.click()
    time.sleep(1)
    # 转发动态文本获取
    text = driver.find_elements_by_class_name('card')
    time.sleep(2)
    for t in text:
        part_text = t.get_attribute('innerText')
        real_t = re.sub('[a-zA-z]', '', part_text)
        list_text.append(real_t)
    list_text = [x for x in list_text if x != '']
    time.sleep(3)
    # 转发动态的id获取
    id = driver.find_elements_by_xpath('//div[@class="post-content repost"]')
    for e in id:
        list_id.append(e.get_attribute('data-ori-did'))
    print(list_id)
    time.sleep(3)
    # 文本日期识别

    for te in list_text:
        try:
            # times = ex.extract_time(te)
            print(te)
            times = time_extract(te)
            list_te = []
            for tim in times:
                list_te.append(tim[5:10])
            print(max(list_te))
            max_t = max(list_te)
            real_time = '2020' + f'{max_t[0:2]}' + f'{max_t[3:5]}'
            rel_time = int(real_time)
            print(real_time)
            list_time.append(rel_time)
            time.sleep(3)
        except:
            list_time.append(20201231)
    '''
    except:
        pass
    '''
    print(list_text)
    print(list_time)
    print(list_id)

    fp = open('./需要删除的id.txt','w',encoding='utf-8')
    wrong_id_list = []
    time_real = 20201112 #当前日期请输入 eg：2020年11月12日写为20201112
    n_id = 0
    for t in list_time:
        if t < time_real:
            #wrong_id_list.append(list_id[n_id])
            fp.write(list_id[n_id])
        else:
            pass
        n_id += 1
    print(wrong_id_list)
    time.sleep(108000)

