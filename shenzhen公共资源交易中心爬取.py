import time
import pandas as pd
import pytesseract
from datetime import datetime, timedelta
import requests
from lxml import html
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine
import numpy as np

def sz():
    urla1 = 'https://www.szggzy.com/cms/api/v1/trade/content/detail?contentId='
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.szggzy.com',
        'Pragma': 'no-cache',
        'Cookie':'Hm_lvt_8a6354d0985601f901cfaa14a7432a14=1694689790,1694764843,1695263058; Hm_lvt_42d6d6c9d2c97bcda19906bdfe55f5c0=1715922545; Hm_lpvt_42d6d6c9d2c97bcda19906bdfe55f5c0=1715922673',
        'Referer': 'https://www.szggzy.com/jygg/list.html?id=jsgc',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    data,data1,data2,data3,data4,data5,data6 = [],[],[],[],[],[],[]
    jieshu = ''
    for i in range(100000):
        time.sleep(1.5)
        json_data = {
            'modelId': 1378,
            'channelId': 2851,
            'fields': [
                {
                    'fieldName': 'jygg_gglxmc_rank1',
                    'fieldValue': '定标公示',
                },
                {
                    'fieldName': 'jygg_gglxmc',
                    'fieldValue': '中标结果公示',
                },
            ],
            'parentBusinessType': '',
            'title': None,
            'releaseTimeBegin': None,
            'releaseTimeEnd': None,
            'page': i,
            'size': 10,
        }
        response = requests.post('https://www.szggzy.com/cms/api/v1/trade/content/page',  headers=headers,  json=json_data).json()
        datas = response['data']['content']
        for ii in datas:
            data0 = {}
            dataid = urla1 + str(ii['id'])
            dataname = ii['title']
            datatime = ii['publishTime']
            date_1 = datetime.strptime(datatime, "%Y-%m-%d %H:%M:%S")
            timestamp_1 = datetime.timestamp(date_1)
            if timestamp_1 <= timestamp_end and timestamp_1 >= timestamp_start:
                data.append(dataid + dataname + datatime)
                print(dataid, dataname, datatime)
                time.sleep(0.5)
                response1 = requests.get(url=dataid, headers=headers).json()
                datatext = response1['data']['txt']
                soup = BeautifulSoup(datatext, 'html.parser')
                tables = soup.find_all('table')
                num_tables = len(tables)
                trs = soup.find_all('tr')
                trs_number = len(trs)
                jk = 0
                for tr in range(len(trs)):
                    tds = trs[tr].find_all('td')
                    if len(tds) == 2:
                        key = tds[0].get_text(strip=True)
                        value = tds[1].get_text(strip=True)
                        data0[key] = value
                    elif len(tds) > 2:
                        if jk == 1:
                            pass
                        elif jk == 0:
                            tdss = trs[tr + 1].find_all('td')
                            tds_number = len(tds)
                            # print(tds,'=======',tdss,len(tds),len(tdss))
                            for tdi in range(tds_number):
                                key = tds[tdi].get_text(strip=True)
                                try:
                                    value = tdss[tdi].get_text(strip=True)
                                    data0[key] = value
                                except:
                                    break
                        jk = 1
                for key in data0.keys():
                    value = data0[key]
                    if '中标价' in key:
                        data5.append(value)
                        print('中标价/万元', value)
                    elif '工期' in key:
                        data2.append(value)
                        print('中标工期', value)
                    elif '招标人' in key or '招标单位' in key or '建设单位' in key:
                        data3.append(value)
                        data6.append(datatime)
                        print('招标人', value)
                    elif '项目名称' in key or '工程名称' in key:
                        data1.append(value)
                        print('项目名称', value)
                    elif '中标人' in key or '单位名称' in key:
                        data4.append(value)
                        print('中标人', value)
                if len(data4) != len(data):
                    soup1 = BeautifulSoup(datatext, 'lxml')
                    text1 = soup1.get_text().replace(" ", "")
                    print(text1)
                    aa = re.findall('工程名称：\s*(.*?)\s*公示日期', text1)[0]
                    bb = re.findall('招标人：\s*(.*?)\s*招标代理机构', text1)[0]
                    cc = re.findall('中标人：\s*(.*?)\s*中标价', text1)[0]
                    dd = re.findall('中标价：\s*(.*?)\s*中标工期', text1)[0]
                    ee = re.findall('中标工期：\s*(.*?)\s*序号', text1)[0]
                    print(aa, bb, cc, dd, ee)
                    data1.append(aa)
                    data2.append(ee)
                    data3.append(bb)
                    data4.append(cc)
                    data5.append(dd)
                    data6.append(datatime)
            elif timestamp_1 < timestamp_start:
                jieshu = '结束'
                break
            elif timestamp_1 > timestamp_end:
                print('本条数据不在时间范围内，不做抓取')
        if jieshu == '结束':
            break
        else:
            pass
    for i in range(len(data4)):
        if ';' in data4[i] or '//' in data4[i] :
            try:
                zhong = data4[i].split(';')
            except:
                zhong = data4[i].split('//')
            for ioi in zhong:
                data1.append(data1[i])
                data2.append(data2[i])
                data3.append(data3[i])
                data4.append(ioi)
                data5.append(data5[i].split('万元')[0])
                data6.append(data6[i])
                data.append(data[i])
        else:
            pass

    df = pd.DataFrame({'项目名称':data1,'备注':data2,'招标人':data3,'中标人':data4,'中标价/万元':data5,'中标时间':data6,'其它':data})
    df['中标时间'] = pd.to_datetime(df['中标时间'])
    print(df.shape)
    df1 = df.sort_values(by=['中标时间'], key=pd.notnull, ascending=[False])
    print(df1,df1.shape)

if __name__ == '__main__':
    # 输入你想要爬取的时间范围
    start_time = '2024-05-01'#开始时间
    end_time = '2024-05-17'#结束时间
    date_start = datetime.strptime(start_time, "%Y-%m-%d")
    date_end = datetime.strptime(end_time, "%Y-%m-%d")
    timestamp_start = datetime.timestamp(date_start)
    timestamp_end = datetime.timestamp(date_end)
    sz()
