#!/usr/bin/env python
# coding: utf-8

"""
@Author: Well
@Date: 2015 - 11 - 09
"""

import time
import datetime
import json
import re
import traceback

import jieba.analyse
import requests


# 数据清洗
def filter_html(html_str):
    # 小尾巴
    tips = '<p>—— 来自TesterHome官方 <a href="http://fir.im/p9vs" target="_blank">安卓客户端</a></p>'
    # 处理换行
    re_br = re.compile('<br\s*?/?>')
    # HTML标签
    re_h = re.compile('</?\w+[^>]*>')
    # url链接
    re_url = re.compile('[a-zA-z]+://[^\s]*')
    # 转义字符
    char_ = {'&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"'}
    html_str = html_str.replace(tips, " ")
    html_str = re_br.sub(" ", html_str)
    html_str = re_h.sub(" ", html_str)
    html_str = re_url.sub(" ", html_str)
    for key_, values_ in char_.iteritems():
        html_str = html_str.replace(key_, values_)
    return html_str


# 获取精华帖列表:  /topics.json ()
# 接口返回分页有问题，放弃用这个接口
# topics_by_excellent_url = "https://testerhome.com/api/v3/topics.json"
# params = dict()
# params["type"] = "popular"
# params["offset"] = 20
# params["limit"] = 20
# topics_by_excellent_resp = requests.get(url=topics_by_excellent_url, timeout=30)
# topics_by_excellent_json = json.loads(topics_by_excellent_resp.content)
# print topics_by_excellent_json


# 爬取帖子数
def get_topics_number():
    base_url = "https://testerhome.com/topics"
    try:
        base_resp = requests.get(url=base_url, timeout=30)
    except:
        traceback.print_exc()
    else:
        html = base_resp.content
        re_type = re.compile(r'<li class="list-group-item">帖子数:(.*?)个</li>')
        result_list = re_type.findall(html)
        if result_list:
            topics_number = int(result_list[0].strip())
            return topics_number


# 获取excellent帖子id列表
def get_excellent_topics_id_list(topics_number):
    print u"获取excellent帖子id列表：开始"

    now = datetime.datetime.now()
    excellent_topics_id_list = list()
    base_api_url = "https://testerhome.com/api/v3/"
    start_number = 1
    sleep_seconds = 0.1
    if isinstance(topics_number, int) and topics_number > 0:
        for topics_id in xrange(start_number, topics_number + 1):
            topics_id_url = "".join((base_api_url, "topics/", str(topics_id), ".json"))
            print u"进度： {0}".format(float((topics_id - start_number + 1)) / (topics_number - start_number + 1))
            try:
                time.sleep(sleep_seconds)
                topics_id_resp = requests.get(url=topics_id_url, timeout=30)
            except:
                traceback.print_exc()
            else:
                if "error" not in topics_id_resp.content:
                    try:
                        topics_id_json = json.loads(topics_id_resp.content)
                    except:
                        traceback.print_exc()
                    else:
                        try:
                            topics_id_json["topic"]["excellent"]
                        except:
                            traceback.print_exc()
                        else:
                            if topics_id_json["topic"]["excellent"]:
                                excellent_topics_id_list.append(topics_id)

    print u"获取excellent帖子id列表：结束"
    print "耗费时间: {0}".format(datetime.datetime.now() - now)
    return excellent_topics_id_list


# 获取某个话题的话题内容
def get_topics_id_content(topics_id):
    if isinstance(topics_id, int) and topics_id > 0:
        # 获取完整的话题内容：/topics/:id.json
        sleep_seconds = 0.1
        base_api_url = "https://testerhome.com/api/v3/"
        topics_id_url = "".join((base_api_url, "topics/", str(topics_id), ".json"))
        try:
            time.sleep(sleep_seconds)
            topics_id_resp = requests.get(url=topics_id_url, timeout=30)
        except:
            traceback.print_exc()
        else:
            if "error" not in topics_id_resp.content:
                try:
                    topics_id_json = json.loads(topics_id_resp.content)
                except:
                    traceback.print_exc()
                else:
                    if "topic" in topics_id_json:
                        if "body_html" in topics_id_json["topic"] and "replies_count" in topics_id_json["topic"]:
                            topics_id_content = topics_id_json["topic"]["body_html"]
                            topics_id_replies_count = topics_id_json["topic"]["replies_count"]
                            return topics_id_content, topics_id_replies_count


# 获取某个话题的全部回帖
def get_topics_id_replies_contents(topics_id, topics_id_replies_count):

    if isinstance(topics_id, int) and topics_id > 0:
        if isinstance(topics_id_replies_count, int) and topics_id_replies_count > 0:
            sleep_seconds = 0.1
            base_api_url = "https://testerhome.com/api/v3/"
            topics_id_replies_limit = 50
            topics_id_replies_page = topics_id_replies_count / topics_id_replies_limit + 1
            topics_id_replies_contents = ""

            for i in xrange(0, topics_id_replies_page):
                # 获取某个话题的回帖列表：/topics/:id/replies.json
                topics_id_replies_url = "".join((base_api_url, "topics/", str(topics_id), "/replies.json"))
                params = dict()
                params["offset"] = i
                params["limit"] = topics_id_replies_limit

                try:
                    time.sleep(sleep_seconds)
                    topics_id_replies_resp = requests.get(url=topics_id_replies_url, timeout=30, params=params)
                except:
                    traceback.print_exc()
                else:
                    try:
                        topics_id_replies_json = json.loads(topics_id_replies_resp.content)
                    except:
                        traceback.print_exc()
                    else:
                        if "replies" in topics_id_replies_json:
                            topics_id_replies_list = topics_id_replies_json["replies"]
                            if isinstance(topics_id_replies_list, list):
                                for j in topics_id_replies_list:
                                    if isinstance(j, dict) and "body_html" in j:
                                        topics_id_replies_contents = " ".join(
                                            (topics_id_replies_contents, j["body_html"]))
                                return topics_id_replies_contents


if __name__ == "__main__":
    print u"分析开始"
    now = datetime.datetime.now()
    excellent_topics_id_list = [134, 136, 139, 143, 150, 153, 154, 155, 160, 163, 167, 171, 175, 182, 189, 191, 194,
                                195, 198, 201, 202, 206, 211, 231, 257, 265, 267, 270, 284, 287, 290, 294, 313, 315,
                                320, 328, 337, 344, 351, 357, 360, 377, 395, 402, 406, 408, 411, 412, 416, 417, 419,
                                451, 453, 456, 457, 461, 462, 465, 470, 476, 477, 478, 479, 482, 484, 486, 487, 488,
                                496, 502, 505, 506, 509, 513, 514, 524, 525, 529, 533, 544, 545, 555, 556, 558, 563,
                                565, 568, 574, 577, 582, 587, 603, 606, 613, 614, 637, 646, 658, 659, 661, 664, 665,
                                678, 680, 682, 692, 704, 711, 714, 726, 733, 749, 782, 813, 818, 824, 833, 834, 842,
                                845, 846, 854, 872, 876, 878, 884, 885, 888, 902, 917, 953, 958, 959, 960, 965, 969,
                                974, 982, 986, 988, 994, 1003, 1007, 1008, 1011, 1013, 1028, 1030, 1034, 1042, 1043,
                                1045, 1047, 1050, 1057, 1061, 1071, 1075, 1078, 1079, 1080, 1090, 1095, 1109, 1113,
                                1128, 1132, 1135, 1145, 1151, 1154, 1159, 1166, 1167, 1170, 1172, 1173, 1192, 1206,
                                1208, 1215, 1221, 1224, 1225, 1229, 1254, 1267, 1269, 1277, 1284, 1294, 1296, 1304,
                                1309, 1310, 1322, 1323, 1325, 1326, 1333, 1336, 1343, 1357, 1358, 1367, 1374, 1376,
                                1378, 1383, 1386, 1389, 1398, 1401, 1419, 1425, 1428, 1432, 1441, 1452, 1462, 1466,
                                1480, 1483, 1491, 1508, 1517, 1520, 1525, 1528, 1539, 1541, 1553, 1569, 1579, 1589,
                                1591, 1598, 1600, 1609, 1610, 1619, 1624, 1631, 1639, 1641, 1642, 1655, 1660, 1662,
                                1663, 1666, 1671, 1677, 1697, 1698, 1713, 1718, 1719, 1723, 1734, 1736, 1739, 1741,
                                1751, 1763, 1769, 1799, 1800, 1801, 1802, 1808, 1809, 1810, 1819, 1826, 1832, 1838,
                                1858, 1863, 1864, 1867, 1871, 1880, 1881, 1887, 1888, 1891, 1896, 1897, 1903, 1919,
                                1934, 1937, 1940, 1942, 1944, 1956, 1957, 1965, 1977, 1980, 1983, 1989, 1999, 2007,
                                2010, 2028, 2029, 2031, 2034, 2041, 2063, 2066, 2068, 2077, 2096, 2110, 2136, 2145,
                                2150, 2157, 2180, 2182, 2184, 2209, 2211, 2213, 2226, 2234, 2235, 2270, 2272, 2276,
                                2289, 2303, 2319, 2322, 2331, 2354, 2363, 2367, 2377, 2382, 2388, 2391, 2407, 2416,
                                2417, 2422, 2427, 2445, 2457, 2461, 2463, 2464, 2475, 2501, 2502, 2510, 2512, 2513,
                                2523, 2534, 2549, 2565, 2572, 2574, 2580, 2583, 2599, 2600, 2606, 2615, 2632, 2643,
                                2648, 2658, 2669, 2671, 2679, 2698, 2714, 2719, 2733, 2757, 2759, 2760, 2761, 2762,
                                2775, 2788, 2805, 2806, 2817, 2824, 2827, 2837, 2840, 2868, 2887, 2889, 2937, 2942,
                                2976, 2984, 2988, 3003, 3009, 3011, 3018, 3019, 3026, 3039, 3045, 3048, 3056, 3062,
                                3063, 3068, 3081, 3096, 3097, 3183, 3196, 3207, 3211, 3257, 3296, 3308, 3312, 3314,
                                3317, 3342, 3344, 3351, 3371, 3394, 3402, 3405, 3407, 3412, 3455, 3457, 3460, 3461,
                                3497, 3503, 3505, 3526, 3533, 3542, 3547, 3556, 3563, 3588, 3594, 3614, 3622, 3633,
                                3638, 3639, 3641, 3671, 3691, 3701, 3711, 3733, 3737, 3750, 3754, 3762, 3765, 3766,
                                3767, 3769, 3776, 3790, 3799, 3800, 3805, 3819, 3824, 3826, 3849, 3857, 3858, 3860,
                                3864, 3881, 3905, 3906, 3912, 3930, 3935]
    # excellent_topics_id_list = [9999, 3935]
    # 抓取范围：1 ~ 3936
    # 获取excellent帖子id列表：耗费时间: 0:13:40.719826, 跑一次即可。
    # topics_number = get_topics_number()
    # excellent_topics_id_list = get_excellent_topics_id_list(topics_number)

    excellent_topics_id_number = len(excellent_topics_id_list)
    print u"社区精华帖的数量为: {0}".format(excellent_topics_id_number)
    print "-" * 20
    topics_all_contents = ""
    for excellent_topics_id in excellent_topics_id_list:
        print u"进度: {0}".format(
            float(excellent_topics_id_list.index(excellent_topics_id) + 1) / excellent_topics_id_number)
        topics_id_content = get_topics_id_content(excellent_topics_id)
        if topics_id_content:
            topics_id_replies_contents = get_topics_id_replies_contents(excellent_topics_id, topics_id_content[1])
            if topics_id_replies_contents:
                topics_all_contents = " ".join((topics_all_contents, topics_id_content[0], topics_id_replies_contents))
            else:
                topics_all_contents = " ".join((topics_all_contents, topics_id_content[0]))

    topics_all_contents = topics_all_contents.encode("utf-8")
    topics_all_contents = filter_html(topics_all_contents)

    print "-" * 20
    results = jieba.analyse.extract_tags(topics_all_contents, topK=20, withWeight=True, allowPOS=())
    print u"基于 TF-IDF 算法的关键词抽取，去掉词性过滤"
    for result in results:
        print u"热词：{0}, 权重值：{1}".format(result[0], result[1])

    print "-" * 20
    results = jieba.analyse.extract_tags(topics_all_contents, topK=20, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
    print u"基于 TF-IDF 算法的关键词抽取，保留词性过滤"
    for result in results:
        print u"热词：{0}, 权重值：{1}".format(result[0], result[1])

    print "-" * 20
    results = jieba.analyse.textrank(topics_all_contents, topK=20, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
    print u"基于 TextRank 算法的关键词抽取"
    for result in results:
        print u"热词：{0}, 权重值：{1}".format(result[0], result[1])

    print u"分析结束，耗费时间：{0}".format(datetime.datetime.now() - now)
