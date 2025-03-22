# Copyright 2025 kailkako/Awesome-Public-Opinion-Analysis-System
# Author：Licheng Yu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==================================================================
# spiderContent.py
# Description: 文章内容爬虫，包括批量爬取和指定文章爬取
# ==================================================================

import re
import time
import requests
import csv
import random
from .clearData import clearData
from globalVariable import *

# 初始化文章内容表格
def init(articleDataFilePath):
    if not os.path.exists(articleDataFilePath):
        with open(articleDataFilePath, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([
                'id',               # 作者id
                'likeNum',          # 点赞数
                'commentsLen',      # 评论数
                'reposts_count',    # 转发量
                'region',           # 地区
                'content',          # 文章内容
                'created_at',       # 发布时间
                'type',             # 文章类型
                'detailUrl',        # followBtnCode>uid + mblogid 文章详情地址
                'authorName',       # 作者名字
                'authorDetail'      # 作者主页地址
            ])

def writerRow(row, articleDataFilePath):
    with open(articleDataFilePath, 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)  # 写入数据到文件
        # 刷新缓冲区
        csvFile.flush()

def get_data(url, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['statuses']
    else:
        return None

# 根据文章类别分类，便于爬虫不同标签的文章，比如 “美食”
def getTypeList(types=[], articleCategoryFilePath=''):
    type_list = []     # 初始化类型列表
    with open(articleCategoryFilePath, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # 检查当前行的第一个元素（文章类型名）是否在指定的类型列表中
            if row[0] in types:
                # 如果存在，则将该行添加到类型列表中
                type_list.append(row)
    return type_list

# 解析 JSON 数据，并将解析后的数据写入文章数据文件
def parse_json(response, articleDataFilePath, type='无'):
    for article in response:
        commentsLen = article['comments_count']
        if int(commentsLen) < 100: break
        id = article['id']
        likeNum = article['attitudes_count']
        reposts_count = article['reposts_count']
        mblogid = article['mblogid']
        try:
            region = article['region_name'].replace('发布于 ', '')
        except:
            region = '无'
        content = article['text']

        # 检查文章内容中是否包含 '...<span class="expand">展开</span>'，表示文章内容需要展开
        if '...<span class="expand">展开</span>' in content:
             # 发送请求获取文章的长文本内容
            response_longTextContent = requests.get(
                'https://weibo.com/ajax/statuses/longtext',
                headers=headers,
                params={'id': mblogid}
            )
            # 如果请求成功，则将文章内容替换为长文本内容
            if response_longTextContent.status_code == 200:
                content = response_longTextContent.json()['data']['longTextContent'] 
        else:
            content = article['text_raw']

        created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')

        type = type
        try:
            detailUrl = 'https://weibo.com/' + str(id) + '/' + str(mblogid) # 构建文章的详情地址
        except:
            detailUrl = '无'
        authorName = article['user']['screen_name']
        authorDetail = 'https://weibo.com/u/' + str(article['user']['id'])

        # 数据清洗
        content = clearData(content)
        # 如果清洗后的内容为空/空格，则跳过该文章
        if content=='': continue
        if content == " ": continue

        # 将解析后的数据写入文章数据文件
        writerRow([
            id,
            likeNum,
            commentsLen,
            reposts_count,
            region,
            content,
            created_at,
            type,
            detailUrl,
            authorName,
            authorDetail
        ], articleDataFilePath)

# 启动批量文章爬虫
def start(types=[], page=0, articleCategoryFilePath='', articleDataFilePath=''):
    articleUrl = 'https://weibo.com/ajax/feed/hottimeline'
    init(articleDataFilePath)
    typeList = getTypeList(types, articleCategoryFilePath)
    print(typeList)
    for type in typeList:
        time.sleep(random.uniform(0, 1))
        for currentPage in range(0, page):
            print('正在爬取的类型：%s 中的第%s页文章数据' % (type[0], currentPage + 1))
            time.sleep(random.uniform(0, 1))  # 随机休眠0-1秒，躲反爬
            parmas = {
                'group_id': type[1],
                'containerid': type[2],
                'max_id': page,
                'count': 10,
                'extparam': 'discover|new_feed'
            }
            response = get_data(articleUrl, parmas)
            parse_json(response, articleDataFilePath, type[0])

# 启动指定单篇文章爬虫
def start_2(url, articleDataFilePath,type):
    init(articleDataFilePath)
    mblogid = getId(url)
    if mblogid is None: return False
    response = requests.get('https://weibo.com/ajax/statuses/show?id=' + mblogid, headers=headers)
    article = response.json()
    articleId = article['id']
    likeNum = article['attitudes_count']
    commentsLen = article['comments_count']
    reposts_count = article['reposts_count']
    try:
        region = article['region_name'].replace('发布于 ', '')
    except:
        region = '无'

    content = article['text']

    if content.find("...<span class=\"expand\">展开</span>") != -1:
        response_longTextContent = requests.get('https://weibo.com/ajax/statuses/longtext', headers=headers,
                                                params={'id': mblogid})
        if response_longTextContent.status_code == 200:
            content = response_longTextContent.json()['data']['longTextContent']
    else:
        content = article['text_raw']

    created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
    if type=='':
        type = '无'
    detailUrl = url
    authorName = article['user']['screen_name']
    authorDetail = 'https://weibo.com/u/' + str(article['user']['id'])

    content = clearData(content)
    if content == "": content = 'error'

    writerRow([
        articleId,
        likeNum,
        commentsLen,
        reposts_count,
        region,
        content,
        created_at,
        type,
        detailUrl,
        authorName,
        authorDetail
    ], articleDataFilePath)

    return articleId

# 获取文章ID
def getId(url):
    '''
       从文章链接中提取文章ID
       在微博网页版点击具体文章发表时间后复制文章链接, 格式形如[https://weibo.com/用户ID/文章ID?pagetype=文章类型]
    '''
    # 找到最后一个斜杠的位置
    last_slash_pos = url.rfind('/')
    # 找到问号的位置
    question_mark_pos = url.find('?', last_slash_pos)
    # 提取斜杠和问号之间的部分
    if last_slash_pos != -1 and question_mark_pos != -1:
        return url[last_slash_pos + 1:question_mark_pos]
    return None
