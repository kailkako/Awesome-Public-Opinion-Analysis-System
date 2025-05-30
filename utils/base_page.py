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
# base_page.py
# Description: 采集主页页面需要的数据
# ==================================================================

from utils.databaseManage import *
from datetime import datetime

allCommentsList = getAllCommentsData()
# articleList = getAllArticleData()

def getHomeTagsData():
    # 获取存储文章内容的列表
    articleList = getAllArticleData()
    
    # 文章个数
    articleLenMax = len(articleList)

    # 最高点赞微博数&作者名
    likeCountMax = 0
    likeCountMaxAuthorName = ''
    # 最多城市
    cityDic = {}
    for article in articleList:
        # 取对应字段比较点赞数，后面有更高的就更新，然后取对应的作者名
        if likeCountMax < int(article[1]):
            likeCountMax = int(article[1])
            likeCountMaxAuthorName = article[9]

        if article[4] != '无':
            if cityDic.get(article[4], -1) == -1: # 尝试获取当前城市在 cityDic 中的值。如果该城市不在字典中，get方法会返回 -1。如果返回值为 -1，说明该城市是第一次出现，将其添加到 cityDic 中，并将其值初始化为 1。
                cityDic[article[4]] = 1
            else:
                cityDic[article[4]] += 1 # 如果返回值不为 -1，说明该城市已经在字典中，将其对应的值加 1。
    cityDicSorted = list(sorted(cityDic.items(), key=lambda x: x[1], reverse=True))
    if articleLenMax==0:
        return 0, '', '',[]
    else:
        return articleLenMax, likeCountMaxAuthorName, cityDicSorted[0][0], articleList

# 获取评论中点赞最高的前四个
def getHomeCommentsLikeCountTopFore():
    return list(sorted(getAllCommentsData(), key=lambda x: int(x[2]), reverse=True))[:4]

# 统计文章的发布日期，返回可绘制时间序列图表的数据
def getHomeArticleCreatedAtChart(articleList):
    if len(articleList)==0 :
        return None,None
    xData = list(set([x[6] for x in articleList]))  # 从articleList里提取每篇文章的发布日期（索引为6）；利用set去除重复的日期
    xData = list(sorted(xData, key=lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp(), reverse=True))  # 降序排列（最新的日期排在前面）
    yData = [0 for x in range(len(xData))]   # 构建一个长度xData相同的列表yData，记录每个日期对应的文章数量
    for article in articleList:
        for index, created_date in enumerate(xData): # 枚举，如果发布时间跟x一样，就+1
            if article[6] == created_date:
                yData[index] += 1
    return xData, yData  # 返回 xData（日期列表）和 yData（每个日期对应的文章数量列表）。

# 统计文章列表中不同类型文章的数量，返回可用于绘制饼图或者柱状图的数据
def getHomeTypeChart(articleList):
    typeDic = {}
    for article in articleList:
        if typeDic.get(article[7], -1) == -1:
            typeDic[article[7]] = 1
        else:
            typeDic[article[7]] += 1
    resultData = []
    for key, value in typeDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData  # 返回文章类型及其对应数量的字典列表

# 文章情绪类别占比
def getEmotion():
    emotionDic = {}
    articleList = getAllArticleData()
    for article in articleList:
        emotion = article[13]
        if emotion not in emotionDic:
            emotionDic[emotion] = 1
        else:
            emotionDic[emotion] += 1
    resultData = []
    for key, value in emotionDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData  # 返回情绪类别及其对应数量的字典列表