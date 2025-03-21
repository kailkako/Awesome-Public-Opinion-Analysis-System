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
# spiderArticleCategory.py
# Description: 爬取文章的类别信息
# ==================================================================

import requests
import csv
import numpy as np
from globalVariable import *

# # 初始化CSV文件，写入表头
def init(articleCategoryFilePath):
    if not os.path.exists(articleCategoryFilePath):
        with open(articleCategoryFilePath, 'w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([
                'typeName',  # 文章类别名
                'gid',
                'containerid'
            ])

# 将数据写入CSV文件
def writerRow(row,articleCategoryFilePath):
    with open(articleCategoryFilePath, 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

# 发送请求获取数据
def get_data(url):
    params = {
        'is_new_segment': 1,
        'fetch_hot': 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 解析爬到的JSON数据并保存到 CSV文件
def parse_json(response,articleCategoryFilePath):
    navList = np.append(response['groups'][3]['group'], response['groups'][4]['group'])
    for nav in navList:
        navName = nav['title']
        gid = nav['gid']
        containerid = nav['containerid']
        writerRow([
            navName,
            gid,
            containerid
        ],articleCategoryFilePath)

# 启动文章类别爬虫
def start(articleCategoryFilePath):
    init(articleCategoryFilePath)
    url = 'https://weibo.com/ajax/feed/allGroups'
    response = get_data(url)
    parse_json(response,articleCategoryFilePath)