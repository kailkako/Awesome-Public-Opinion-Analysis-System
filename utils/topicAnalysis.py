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
# topicAnalysis.py
# Description: 针对微博热搜话题相关的分析功能
# ==================================================================

import json
import matplotlib.pyplot as plt
import requests
from wordcloud import WordCloud
from globalVariable import headers

# 从微博热门搜索接口获取热门话题列表，并返回前20个话题
def getCiTiaoList():
    '''实现：使用 requests 库发送 GET 请求，解析返回的 JSON 数据，提取话题名称。'''
    response = requests.get('https://weibo.com/ajax/side/hotSearch', headers=headers)  # 开发者工具监控网络可以找到入口，headers用于反爬虫（设置了cookie和user-agent）
    text = response.json()  # 解析json
    realtime_list = text['data']['realtime'] # 提取data里的realtime字段
    word_scheme_list = [entry['word_scheme'].strip('#') for entry in realtime_list if 'word_scheme' in entry] # 提取word_scheme字段(就是#+热搜话题名字)，并去掉#
    return word_scheme_list[:20]  # 返回前20个话题名

# 对指定话题进行分析，获取话题的相关信息，如概述、情感占比、词云数据和典型观点
def getWeiboAI(topicName):
    '''实现：发送 GET 请求到微博智搜分析接口，解析返回的 JSON 数据，提取所需信息。'''
    response = requests.get('https://ai.s.weibo.com/api/llm/analysis_tab.json?query=' + topicName, headers=headers)
    content = response.json()
    data = content['data']
    description = data['past_events']['desc']
    description_list = description.split('\n')
    emotion = data['stars']['desc']
    word_cloud = data['word_cloud']['desc']
    typical_viewpoint = data['typical_viewpoint']['desc']
    typical_viewpoint = typical_viewpoint.replace("**", "")  # 去掉Markdown格式
    typical_viewpoint_list = typical_viewpoint.split('\n')
    return description_list, emotion, word_cloud, typical_viewpoint_list

# 根据词云数据生成词云图
def generate_wordcloud(data, topicName):
    # 将 JSON 字符串转换为 Python 对象
    data_list = json.loads(data)
    # 创建词频字典
    word_freq = {item['name']: item['value'] for item in data_list}
    # 生成词云
    wordcloud = WordCloud(font_path='msyh.ttc', width=800, height=400,
                          background_color='white').generate_from_frequencies(word_freq)
    # 保存词云图
    wordCloudPath='static/WordCloud_toplc/' + topicName + '.png'
    wordcloud.to_file(wordCloudPath)
    return True

# 解析情感占比数据，提取名称和数值
def getCharData(data_str):
    data = json.loads(data_str)
    names = [item['name'] for item in data]
    nums = [item['num'] for item in data]
    print(names)
    print(nums)
    return names, nums
