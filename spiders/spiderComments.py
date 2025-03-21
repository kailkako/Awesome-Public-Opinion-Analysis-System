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
# spiderComments.py
# Description: 评论爬虫
# ==================================================================

import random
import time
import requests
import csv
from .clearData import clearData
from globalVariable import *
from datetime import datetime
from utils.wordCloudPicture import get_img

text = ''       # 存储评论内容
max_id = ''     # 存储最大评论 ID
articleId = ''  # 存储文章 ID
commentUrl = 'https://weibo.com/ajax/statuses/buildComments' # 微博评论 URL，发送请求获取评论数

# 初始化评论文件
def init(articleCommentsFilePath):
     # 检查文件是否存在，如果不存在则创建并写入表头
    if not os.path.exists(articleCommentsFilePath):
        with open(articleCommentsFilePath, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([
                'articleId',
                'created_at',
                'likes_counts',
                'region',
                'content',
                'authorName',
                'authorGender',
                'authorAddress'
            ])

def writerRow(row, articleCommentsFilePath):
    with open(articleCommentsFilePath, 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
        csvFile.flush()
        csvFile.close()

# 发送请求获取评论数据
def get_data(url, params):
     # 设置请求头
    response = requests.get(url, headers=headers, params=params)
    # 检查响应状态码是否为 200（是否成功访问）
    if response.status_code == 200:
        # 将响应内容转换为 JSON 格式
        response_json = response.json()
        # 更新最大评论 ID
        global max_id
        max_id = response_json['max_id']
        # 返回评论数据
        return response_json['data']
    else:
        return None

# 把所有文章数据从文件读到列表
def getAllArticleList(articleDataFilePath):
    artileList = []
    # 打开文章数据文件
    with open(articleDataFilePath, 'r', encoding='utf-8') as reader:
        # 刷新文件缓冲区
        reader.flush()
        # 创建 CSV 读取器
        readerCsv = csv.reader(reader)
        # 遍历每一行数据
        for nav in readerCsv:
            # 将每行数据添加到文章列表中
            artileList.append(nav)
    return artileList


# 解析评论数据并写入文件
def parse_json(response, articleId, articleCommentsFilePath):
    if response is None: return
    # 遍历每条评论
    for comment in response:

        # 将评论创建时间转换为指定格式
        created_at = datetime.strptime(comment['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        # 获取评论点赞数
        likes_counts = comment['like_counts']
        
        # 获取评论发布地区
        global region
        try:
            region = comment['source'].replace('来自', '')
        except:
            region = '未知'

        # 处理评论内容
        content = comment['text_raw']
        # 调用数据清洗函数
        content = clearData(content)
        # 检查评论内容是否为空，为空就跳出，开始下一条评论
        if content == "": continue
        
        global text
        text += content
        authorName = comment['user']['screen_name'] # 获取评论作者姓名
        authorGender = comment['user']['gender']    # 获取评论作者性别
        authorAddress = comment['user']['location'] # 获取评论作者地址

        # 将评论数据写入 CSV 文件
        writerRow([
            articleId,
            created_at,
            likes_counts,
            region,
            content,
            authorName,
            authorGender,
            authorAddress
        ], articleCommentsFilePath)


# 启动文章类别爬虫
def start(articleDataFilePath, articleCommentsFilePath):
    # 初始化评论文件
    init(articleCommentsFilePath)
    # 获取所有文章列表
    articleList = getAllArticleList(articleDataFilePath)
    # 遍历每篇文章
    for article in articleList[1:]:
        global articleId
        # 获取文章 ID
        articleId = article[0]
        global text
        text = ''
        # 记录开始时间
        start_time = time.time()
        print('正在爬取id值为%s的文章评论' % articleId)
        # 随机休眠一段时间，避免被反爬机制检测
        time.sleep(random.uniform(0, 1))
        # 设置请求参数
        params = {
            'id': int(articleId),
            'is_show_bulletin': 2
        }
        # 发送请求获取评论数据
        response = get_data(commentUrl, params)
        # 解析评论数据并写入文件
        parse_json(response, articleId, articleCommentsFilePath)
        # 设置最大翻页次数
        max_page = 100
        max_id_last = 0
        # 循环获取更多评论数据
        while max_id != 0:
            max_page -= 1
            if max_page < 0:
                break
            print(max_id)
            if max_id_last == max_id: break
            max_id_last = max_id
            # 更新请求参数
            params = {
                'id': int(articleId),
                'is_show_bulletin': 2,
                'max_id': int(max_id)
            }
            # 发送请求获取评论数据
            response = get_data(commentUrl, params)
            # 解析评论数据并写入文件
            parse_json(response, articleId, articleCommentsFilePath)
            # 随机休眠一段时间，避免被反爬机制检测
            time.sleep(random.uniform(0, 0.5))
        # 记录结束时间
        end_time = time.time()
        print('耗时：' + str(end_time - start_time))
        print()
        # 调用获取图片函数
        get_img(articleId, text)