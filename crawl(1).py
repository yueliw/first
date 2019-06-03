#参考 https://www.cnblogs.com/eastonliu/p/9925652.html 字体反爬
#参考 https://blog.csdn.net/xinkexueguanli/article/details/52552132 爬虫部分
from bs4 import BeautifulSoup
import re
import base64
import io
import requests
import csv
import time
import lxml
from fontTools.ttLib import TTFont

url = "https://wh.58.com/pinpaigongyu/pn/%7Bpage%7D/?minprice={}"

#已完成的页数序号，初时为0
rmoney = '500_700'
i=701

csv_file = open("rent.csv","w",newline='') 
csv_writer = csv.writer(csv_file, delimiter=',')
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

while True:
    rmoney = str(i)+'_'+str(i+200)
    i+=200
    print("fetch: ", url.format(rmoney))
    time.sleep(1)
    response = requests.get(url.format(rmoney),headers=headers)
    
    base64_str = re.search("base64,(.*?)'\)",response.text).group(1)  #获取加密码，并转化为字典
    b = base64.b64decode(base64_str)
    font = TTFont(io.BytesIO(b))
    bestcmap = font['cmap'].getBestCmap()
    newmap = dict()
    for key in bestcmap.keys():
        value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
        key = hex(key)
        newmap[key] = value
        
    # 把页面上自定义字体替换成正常字体
    response_ = response.text
    for key,value in newmap.items():
        key_ = key.replace('0x','&#x') + ';'
        if key_ in response_:
            response_ = response_.replace(key_,str(value))
            
    html = BeautifulSoup(response_,features="lxml")
    house_list = html.select(".list > li")
    
    # 循环在读不到新的房源时结束
    if not house_list or i >= 4101:
        break
        
    for house in house_list:
        house_title = house.select("h2")[0].string
        house_url = house.select("a")[0]["href"]
        house_info_list = house_title.split()

        # 如果第二列是公寓名则取第一列作为地址
        if "公寓" in house_info_list[1] or "青年社区" in house_info_list[1]:
            house_location = house_info_list[0]
        else:
            house_location = house_info_list[1]
            
        text = house.select(".money")[0].select("b")[0].string

        house_money=text
        csv_writer.writerow([house_title, house_location, house_money, house_url])
        
csv_file.close() 
