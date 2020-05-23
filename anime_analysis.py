import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import os


# 获取Top100动漫的id
def get_ids():

    """
    1、下面的cookies信息和header信息填一下，反爬，防止被封，在榜单页面F12查看NetWork里的html信息，可以直接复制 curl链接，
通过一个网站工具可以直接转换成Python形式的请求：这个转换不懂的话可以参考这篇文章：https://mp.weixin.qq.com/s/fVDwNdVDZo_0q6jAMWCGAA

2、对Python感兴趣的同学可以关注我的个人公众号「Python知识圈」，有疑问也可以通过公众号加我微信，一起探讨交流
"""
    
    cookies = {
        xxx
    }

    headers = {
        'xxx'
    }
    ids = []
    response_one = requests.get('http://movie.mtime.com/list/1709.html', headers=headers, cookies=cookies,
                            verify=False)
    html_one = response_one.text
    soup_one = BeautifulSoup(html_one, 'lxml')
    id_info = soup_one.select('div[class="top_nlist"]')
    patt = r'<a href="http://movie.mtime.com/(\d+)/'
    id_one = re.findall(patt, str(id_info), re.DOTALL)
    for item in id_one:
        ids.append(item)
    for num in range(2, 11):
        response = requests.get('http://movie.mtime.com/list/1709-{}.html'.format(num), headers=headers, cookies=cookies, verify=False)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        id_info = soup.select('div[class="top_nlist"]')
        patt = r'<a href="http://movie.mtime.com/(\d+)/'
        id_one = re.findall(patt, str(id_info), re.DOTALL)
        for item in id_one:
            ids.append(item)
    return ids


# 获取电影的票房和评分信息
def get_box_office(id):
    url = 'http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_' \
          'CallBackMethod=GetMovieOverviewRating&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%' \
          '2F{}%2F&Ajax_CallBackArgument0={}'.format(id, id)
    headers = {'user-agent': '查看自己电脑浏览器的user-agent，放在此处'}
    html = requests.get(url, headers=headers).text
    json_info = html.split('=')[-1].replace(';', '')
    info = json.loads(json_info)
    try:
        RatingFinal = info['value']['movieRating']['RatingFinal']
        TotalBoxOffice = info['value']['boxOffice']['TotalBoxOffice'] + info['value']['boxOffice']['TotalBoxOfficeUnit']
        FirstDayBoxOffice = info['value']['boxOffice']['FirstDayBoxOffice'] + info['value']['boxOffice']['FirstDayBoxOfficeUnit']
    except Exception as e:
        pass
        RatingFinal = ''
        TotalBoxOffice = ''
        FirstDayBoxOffice = ''
    return RatingFinal, FirstDayBoxOffice, TotalBoxOffice  # 评分、首日票房、总票房


# 获取动漫的导演和编剧等信息
def get_movie_info(id):

    # 获取登陆后的cookies和headers信息，反爬，防止被封
    cookies = {
        'xxx',
    }
    headers = {
        'xxx',
    }
    response = requests.get('http://movie.mtime.com/{}/'.format(id), headers=headers, cookies=cookies)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')
    info_name = soup.select('dd[pan="M14_Movie_Overview_BaseInfo"]')
    info_names = re.findall(r'</strong>(.*?)</a>', str(info_name), re.DOTALL)
    i = 0
    data = []
    try:
        director = str(info_names[0]).split('target="_blank">')[-1]     # 导演
        playwriter = str(info_names[1]).split('target="_blank">')[-1]   # 编剧
        section = str(info_names[2]).split('target="_blank">')[-1]      # 发行地区
        company = str(info_names[3]).split('target="_blank">')[-1]      # 发行公司
        other = re.findall(r'更多片名：</strong>(.*?)</span>', str(info_name), re.DOTALL)   # 更多片名
        other_name = str(other).split('<span>')[-1].split('\'')[0]      # 更多片名
        movie_info = soup.select('div[class="db_cover __r_c_"]')
        movie_name = re.findall(r'title="(.*?)">', str(movie_info), re.DOTALL)  # 提取电影名称
        movie_title = movie_name[0]
        RatingFinal, FirstDayBoxOffice, TotalBoxOffice = get_box_office(id)

        info = {}
        info['电影名'] = movie_title
        info['导演'] = director
        info['编剧'] = playwriter
        info['国家地区'] = section
        info['发行公司'] = company
        info['更多片名'] = other_name
        info['评分'] = RatingFinal
        info['首日票房'] = FirstDayBoxOffice
        info['总票房'] = TotalBoxOffice
        data.append(info)
    except IndexError:
        pass
    return data


def write2csv(id):
    data = get_movie_info(id)
    out_file = r'./日本动画电影时光网评分TOP100.csv'
    with open(out_file, 'a', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['电影名', '导演', '编剧', '国家地区', '发行公司', '更多片名', '评分', '首日票房', '总票房']  # 控制列的顺序
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        with open(out_file, "r", newline="", encoding='utf-8') as file:   # 读取信息，若存在表头，就不会重复写入表头
            reader = csv.reader(file)
            if not [row for row in reader]:
                writer.writeheader()
                writer.writerows(data)
            else:
                writer.writerows(data)
        print("追加写入成功")
    print("全部写入保存成功")


if __name__ == '__main__':
    ids = get_ids()
    print(ids)
    for id in ids:
        write2csv(id)

